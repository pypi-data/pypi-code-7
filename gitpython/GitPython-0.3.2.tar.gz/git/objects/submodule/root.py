from base import Submodule, UpdateProgress
from util import (
                    find_first_remote_branch
                )
from git.exc import InvalidGitRepositoryError
import git

import sys

__all__ = ["RootModule", "RootUpdateProgress"]


class RootUpdateProgress(UpdateProgress):
    """Utility class which adds more opcodes to the UpdateProgress"""
    REMOVE, PATHCHANGE, BRANCHCHANGE, URLCHANGE = [1 << x for x in range(UpdateProgress._num_op_codes, UpdateProgress._num_op_codes+4)]
    _num_op_codes = UpdateProgress._num_op_codes+4
    
    __slots__ = tuple()

BEGIN = RootUpdateProgress.BEGIN
END = RootUpdateProgress.END
REMOVE = RootUpdateProgress.REMOVE
BRANCHCHANGE = RootUpdateProgress.BRANCHCHANGE
URLCHANGE = RootUpdateProgress.URLCHANGE
PATHCHANGE = RootUpdateProgress.PATHCHANGE

class RootModule(Submodule):
    """A (virtual) Root of all submodules in the given repository. It can be used
    to more easily traverse all submodules of the master repository"""
    
    __slots__ = tuple()
    
    k_root_name = '__ROOT__'
    
    def __init__(self, repo):
        # repo, binsha, mode=None, path=None, name = None, parent_commit=None, url=None, ref=None)
        super(RootModule, self).__init__(
                                        repo, 
                                        binsha = self.NULL_BIN_SHA, 
                                        mode = self.k_default_mode, 
                                        path = '', 
                                        name = self.k_root_name, 
                                        parent_commit = repo.head.commit,
                                        url = '',
                                        branch_path = git.Head.to_full_path(self.k_head_default)
                                        )
        
    
    def _clear_cache(self):
        """May not do anything"""
        pass
    
    #{ Interface 
    
    def update(self, previous_commit=None, recursive=True, force_remove=False, init=True, 
                    to_latest_revision=False, progress=None, dry_run=False):
        """Update the submodules of this repository to the current HEAD commit.
        This method behaves smartly by determining changes of the path of a submodules
        repository, next to changes to the to-be-checked-out commit or the branch to be 
        checked out. This works if the submodules ID does not change.
        Additionally it will detect addition and removal of submodules, which will be handled
        gracefully.
        
        :param previous_commit: If set to a commit'ish, the commit we should use 
            as the previous commit the HEAD pointed to before it was set to the commit it points to now. 
            If None, it defaults to HEAD@{1} otherwise
        :param recursive: if True, the children of submodules will be updated as well
            using the same technique
        :param force_remove: If submodules have been deleted, they will be forcibly removed.
            Otherwise the update may fail if a submodule's repository cannot be deleted as 
            changes have been made to it (see Submodule.update() for more information)
        :param init: If we encounter a new module which would need to be initialized, then do it.
        :param to_latest_revision: If True, instead of checking out the revision pointed to 
            by this submodule's sha, the checked out tracking branch will be merged with the 
            newest remote branch fetched from the repository's origin
        :param progress: RootUpdateProgress instance or None if no progress should be sent
        :param dry_run: if True, operations will not actually be performed. Progress messages
            will change accordingly to indicate the WOULD DO state of the operation."""
        if self.repo.bare:
            raise InvalidGitRepositoryError("Cannot update submodules in bare repositories")
        # END handle bare
        
        if progress is None:
            progress = RootUpdateProgress()
        #END assure progress is set
        
        prefix = ''
        if dry_run:
            prefix = 'DRY-RUN: '
        
        repo = self.repo
        
        # SETUP BASE COMMIT
        ###################
        cur_commit = repo.head.commit
        if previous_commit is None:
            try:
                previous_commit = repo.commit(repo.head.log_entry(-1).oldhexsha)
                if previous_commit.binsha == previous_commit.NULL_BIN_SHA:
                    raise IndexError
                #END handle initial commit
            except IndexError:
                # in new repositories, there is no previous commit
                previous_commit = cur_commit
            #END exception handling
        else:
            previous_commit = repo.commit(previous_commit)   # obtain commit object 
        # END handle previous commit
        
        
        psms = self.list_items(repo, parent_commit=previous_commit)
        sms = self.list_items(repo)
        spsms = set(psms)
        ssms = set(sms)
        
        # HANDLE REMOVALS
        ###################
        rrsm = (spsms - ssms)
        len_rrsm = len(rrsm)
        for i, rsm in enumerate(rrsm):
            op = REMOVE
            if i == 0:
                op |= BEGIN
            #END handle begin
            
            # fake it into thinking its at the current commit to allow deletion
            # of previous module. Trigger the cache to be updated before that
            progress.update(op, i, len_rrsm, prefix+"Removing submodule %r at %s" % (rsm.name, rsm.abspath))
            rsm._parent_commit = repo.head.commit
            if not dry_run:
                rsm.remove(configuration=False, module=True, force=force_remove)
            #END handle dry-run
            
            if i == len_rrsm-1:
                op |= END
            #END handle end
            progress.update(op, i, len_rrsm, prefix+"Done removing submodule %r" % rsm.name)
        # END for each removed submodule
        
        # HANDLE PATH RENAMES
        #####################
        # url changes + branch changes
        csms = (spsms & ssms)
        len_csms = len(csms)
        for i, csm in enumerate(csms):
            psm = psms[csm.name]
            sm = sms[csm.name]
            
            #PATH CHANGES
            ##############
            if sm.path != psm.path and psm.module_exists():
                progress.update(BEGIN|PATHCHANGE, i, len_csms, prefix+"Moving repository of submodule %r from %s to %s" % (sm.name, psm.abspath, sm.abspath))  
                # move the module to the new path
                if not dry_run:
                    psm.move(sm.path, module=True, configuration=False)
                #END handle dry_run
                progress.update(END|PATHCHANGE, i, len_csms, prefix+"Done moving repository of submodule %r" % sm.name)
            # END handle path changes
            
            if sm.module_exists():
                # HANDLE URL CHANGE
                ###################
                if sm.url != psm.url:
                    # Add the new remote, remove the old one
                    # This way, if the url just changes, the commits will not 
                    # have to be re-retrieved
                    nn = '__new_origin__'
                    smm = sm.module()
                    rmts = smm.remotes
                    
                    # don't do anything if we already have the url we search in place
                    if len([r for r in rmts if r.url == sm.url]) == 0:
                        progress.update(BEGIN|URLCHANGE, i, len_csms, prefix+"Changing url of submodule %r from %s to %s" % (sm.name, psm.url, sm.url))
                        
                        if not dry_run:
                            assert nn not in [r.name for r in rmts]
                            smr = smm.create_remote(nn, sm.url)
                            smr.fetch(progress=progress)
                            
                            # If we have a tracking branch, it should be available
                            # in the new remote as well.
                            if len([r for r in smr.refs if r.remote_head == sm.branch_name]) == 0:
                                raise ValueError("Submodule branch named %r was not available in new submodule remote at %r" % (sm.branch_name, sm.url))
                            # END head is not detached
                            
                            # now delete the changed one
                            rmt_for_deletion = None
                            for remote in rmts:
                                if remote.url == psm.url:
                                    rmt_for_deletion = remote
                                    break
                                # END if urls match
                            # END for each remote
                            
                            # if we didn't find a matching remote, but have exactly one, 
                            # we can safely use this one
                            if rmt_for_deletion is None:
                                if len(rmts) == 1:
                                    rmt_for_deletion = rmts[0]
                                else:
                                    # if we have not found any remote with the original url
                                    # we may not have a name. This is a special case, 
                                    # and its okay to fail here
                                    # Alternatively we could just generate a unique name and leave all
                                    # existing ones in place
                                    raise InvalidGitRepositoryError("Couldn't find original remote-repo at url %r" % psm.url)
                                #END handle one single remote
                            # END handle check we found a remote
                            
                            orig_name = rmt_for_deletion.name
                            smm.delete_remote(rmt_for_deletion)
                            # NOTE: Currently we leave tags from the deleted remotes
                            # as well as separate tracking branches in the possibly totally 
                            # changed repository ( someone could have changed the url to 
                            # another project ). At some point, one might want to clean
                            # it up, but the danger is high to remove stuff the user
                            # has added explicitly
                            
                            # rename the new remote back to what it was
                            smr.rename(orig_name)
                            
                            # early on, we verified that the our current tracking branch
                            # exists in the remote. Now we have to assure that the 
                            # sha we point to is still contained in the new remote
                            # tracking branch.
                            smsha = sm.binsha
                            found = False
                            rref = smr.refs[self.branch_name]
                            for c in rref.commit.traverse():
                                if c.binsha == smsha:
                                    found = True
                                    break
                                # END traverse all commits in search for sha
                            # END for each commit
                            
                            if not found:
                                # adjust our internal binsha to use the one of the remote
                                # this way, it will be checked out in the next step
                                # This will change the submodule relative to us, so 
                                # the user will be able to commit the change easily
                                print >> sys.stderr, "WARNING: Current sha %s was not contained in the tracking branch at the new remote, setting it the the remote's tracking branch" % sm.hexsha
                                sm.binsha = rref.commit.binsha
                            #END reset binsha
                            
                            #NOTE: All checkout is performed by the base implementation of update
                        #END handle dry_run
                        progress.update(END|URLCHANGE, i, len_csms, prefix+"Done adjusting url of submodule %r" % (sm.name))
                    # END skip remote handling if new url already exists in module
                # END handle url
                
                # HANDLE PATH CHANGES
                #####################
                if sm.branch_path != psm.branch_path:
                    # finally, create a new tracking branch which tracks the 
                    # new remote branch
                    progress.update(BEGIN|BRANCHCHANGE, i, len_csms, prefix+"Changing branch of submodule %r from %s to %s" % (sm.name, psm.branch_path, sm.branch_path))
                    if not dry_run:
                        smm = sm.module()
                        smmr = smm.remotes
                        try:
                            tbr = git.Head.create(smm, sm.branch_name, logmsg='branch: Created from HEAD')
                        except OSError:
                            # ... or reuse the existing one
                            tbr = git.Head(smm, sm.branch_path)
                        #END assure tracking branch exists
                        
                        tbr.set_tracking_branch(find_first_remote_branch(smmr, sm.branch_name))
                        # figure out whether the previous tracking branch contains
                        # new commits compared to the other one, if not we can 
                        # delete it.
                        try:
                            tbr = find_first_remote_branch(smmr, psm.branch_name)
                            if len(smm.git.cherry(tbr, psm.branch)) == 0:
                                psm.branch.delete(smm, psm.branch)
                            #END delete original tracking branch if there are no changes
                        except InvalidGitRepositoryError:
                            # ignore it if the previous branch couldn't be found in the
                            # current remotes, this just means we can't handle it
                            pass
                        # END exception handling
                        
                        #NOTE: All checkout is done in the base implementation of update
                    #END handle dry_run
                    
                    progress.update(END|BRANCHCHANGE, i, len_csms, prefix+"Done changing branch of submodule %r" % sm.name)
                #END handle branch
            #END handle 
        # END for each common submodule 
        
        # FINALLY UPDATE ALL ACTUAL SUBMODULES
        ######################################
        for sm in sms:
            # update the submodule using the default method
            sm.update(recursive=False, init=init, to_latest_revision=to_latest_revision, 
                        progress=progress, dry_run=dry_run)
            
            # update recursively depth first - question is which inconsitent 
            # state will be better in case it fails somewhere. Defective branch
            # or defective depth. The RootSubmodule type will never process itself, 
            # which was done in the previous expression
            if recursive:
                # the module would exist by now if we are not in dry_run mode
                if sm.module_exists():
                    type(self)(sm.module()).update( recursive=True, force_remove=force_remove, 
                                                    init=init, to_latest_revision=to_latest_revision,
                                                    progress=progress, dry_run=dry_run)
                #END handle dry_run
            #END handle recursive
        # END for each submodule to update

    def module(self):
        """:return: the actual repository containing the submodules"""
        return self.repo
    #} END interface
#} END classes
