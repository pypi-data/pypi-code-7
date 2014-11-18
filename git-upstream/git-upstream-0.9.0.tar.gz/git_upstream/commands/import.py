#
# Copyright (c) 2012, 2013, 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from git_upstream.errors import GitUpstreamError
from git_upstream.log import LogDedentMixin
from git_upstream.lib.utils import GitMixin
from git_upstream.lib.rebaseeditor import RebaseEditor
from git_upstream import subcommand, log
from git_upstream.lib.searchers import UpstreamMergeBaseSearcher

from abc import ABCMeta, abstractmethod
from collections import Sequence
from git import GitCommandError

import inspect


class ImportUpstreamError(GitUpstreamError):
    """Exception thrown by L{ImportUpstream}"""
    pass


class ImportUpstream(LogDedentMixin, GitMixin):
    """
    Import code from an upstream project and merge in additional branches
    to create a new branch unto which changes that are not upstream but are
    on the local branch are applied.
    """

    def __init__(self, branch=None, upstream=None, import_branch=None,
                 extra_branches=None, *args, **kwargs):
        if not extra_branches:
            extra_branches = []
        self._branch = branch
        self._upstream = upstream
        self._import_branch = import_branch
        self._extra_branches = extra_branches

        # make sure to correctly initialise inherited objects before performing
        # any computation
        super(ImportUpstream, self).__init__(*args, **kwargs)

        # test that we can use this git repo
        if not self.is_detached():
            raise ImportUpstreamError("In 'detached HEAD' state")

        if self.repo.bare:
            raise ImportUpstreamError("Cannot perform imports in bare repos")

        if self.branch == 'HEAD':
            self._branch = str(self.repo.active_branch)

        # validate branches exist and log all failures
        branches = [
            self.branch,
            self.upstream
        ]
        branches.extend(self.extra_branches)

        invalid_ref = False
        for branch in branches:
            if not any(head for head in self.repo.heads
                       if head.name == branch):
                msg = "Specified ref does not exist: '%s'"
                self.log.error(msg, branch)
                invalid_ref = True

        if invalid_ref:
            raise ImportUpstreamError("Invalid ref")

    @property
    def branch(self):
        """Branch to search for branch changes to apply when importing."""
        return self._branch

    @property
    def upstream(self):
        """Branch containing the upstream project code base to track."""
        return self._upstream

    @property
    def import_branch(self):
        """
        Pattern to use to generate the name, or user specified branch name
        to use for import.
        """
        return self._import_branch

    @property
    def extra_branches(self):
        """
        Branch containing the additional branches to be merged with the
        upstream when importing.
        """
        return self._extra_branches

    def _set_branch(self, branch, commit, checkout=False, force=False):

        if str(self.repo.active_branch) == branch:
            self.log.info(
                """\
                Resetting branch '%s' to specified commit '%s'
                    git reset --hard %s
                """, branch, commit, commit)
            self.git.reset(commit, hard=True)
        elif checkout:
            if force:
                checkout_opt = '-B'
            else:
                checkout_opt = '-b'

            self.log.info(
                """\
                Checking out branch '%s' using specified commit '%s'
                    git checkout %s %s %s
                """, branch, commit, checkout_opt, branch, commit)
            self.git.checkout(checkout_opt, branch, commit)
        else:
            self.log.info(
                """\
                Creating  branch '%s' from specified commit '%s'
                    git branch --force %s %s
                """, branch, commit, branch, commit)
            self.git.branch(branch, commit, force=force)

    def create_import(self, commit=None, import_branch=None, checkout=False,
                      force=False):
        """
        Create the import branch from the specified commit.

        If the branch already exists abort if force is false
            If current branch, reset the head to the specified commit
            If checkout is true, switch and reset the branch to the commit
            Otherwise just reset the branch to the specified commit
        If the branch doesn't exist, create it and switch to it
        automatically if checkout is true.
        """

        if not commit:
            commit = self.upstream

        try:
            self.git.show_ref(commit, quiet=True, heads=True)

        except GitCommandError as e:
            msg = "Invalid commit '%s' specified to import from"
            self.log.error(msg, commit)
            raise ImportUpstreamError((msg + ": %s"), commit, e)

        if not import_branch:
            import_branch = self.import_branch

        # use describe in order to be certain about unique identifying 'commit'
        # Create a describe string with the following format:
        #    <describe upstream>[-<extra branch abbref hash>]*
        #
        # Simply appends the 7 character ref abbreviation for each extra branch
        # prefixed with '-', for each extra branch in the order they are given.
        describe_commit = self.git.describe(commit, tags=True,
                                            with_exceptions=False)
        if not describe_commit:
            self.log.warning("No tag describes the upstream branch")
            describe_commit = self.git.describe(commit, always=True, tags=True)

        self.log.info("""\
                    Using '%s' to describe:
                        %s
                    """, describe_commit, commit)
        describe_branches = [describe_commit]

        describe_branches.extend([self.git.rev_parse(b, short=True)
                                  for b in self.extra_branches])
        import_describe = "-".join(describe_branches)
        self._import_branch = self.import_branch.format(
            describe=import_describe)

        self._import_branch = import_branch.format(describe=import_describe)
        base = self._import_branch + "-base"
        self.log.debug("Creating and switching to import branch base '%s' "
                       "created from '%s' (%s)", base, self.upstream, commit)

        self.log.info(
            """\
            Checking if import branch '%s' already exists:
                git branch --list %s
            """, base, base)
        if self.git.show_ref("refs/heads/" + base, verify=True,
                             with_exceptions=False) and not force:
            msg = "Import branch '%s' already exists, set 'force' to replace"
            self.log.error(msg, self.import_branch)
            raise ImportUpstreamError(msg % self.import_branch)

        self._set_branch(base, commit, checkout, force)

        if self.extra_branches:
            self.log.info(
                """\
                Merging additional branch(es) '%s' into import branch '%s'
                    git checkout %s
                    git merge %s
                """, ", ".join(self.extra_branches), base, base,
                " ".join(self.extra_branches))
            self.git.checkout(base)
            self.git.merge(*self.extra_branches)

    def _linearise(self, branch, sequence, previous_import):

        counter = len(sequence) - 1
        ancestors = set()

        self._set_branch(branch, previous_import, checkout=True, force=True)
        root = previous_import.hexsha
        while counter > 0:
            # add commit to list of ancestors to check
            ancestors.add(root)

            # look for merge commits that are not part of ancestry path
            for idx in xrange(counter - 1, -1, -1):
                commit = sequence[idx]
                # if there is only one parent, no need to check the others
                if len(commit.parents) < 2:
                    ancestors.add(commit.hexsha)
                elif any(p.hexsha not in ancestors for p in commit.parents):
                    self.log.debug("Rebase upto commit SHA1: %s",
                                   commit.hexsha)
                    idx = idx + 1
                    break
                else:
                    ancestors.add(commit.hexsha)
            tip = sequence[idx].hexsha

            self.log.info("Rebasing from %s to %s", root, tip)
            previous = self.git.rev_parse(branch)
            self.log.info("Rebasing onto '%s'", previous)
            if root == previous and idx == 0:
                # special case, we are already linear
                self.log.info("Already in a linear layout")
                return
            self._set_branch(branch, tip, force=True)
            try:
                self.log.debug(
                    """\
                        git rebase -p --onto=%s \\
                            %s %s
                    """, previous, root, branch)
                self.git.rebase(root, branch, onto=previous, p=True)
            except:
                self.git.rebase(abort=True, with_exceptions=False)
                raise
            counter = idx - 1
            # set root commit for next loop
            root = sequence[counter].hexsha

    def apply(self, strategy, interactive=False):
        """Apply list of commits given onto latest import of upstream"""

        commit_list = list(strategy.filtered_iter())
        if len(commit_list) == 0:
            self.log.notice("There are no local changes to be applied!")
            return False

        self.log.debug(
            """\
            Should apply the following list of commits
                %s
            """, "\n    ".join([c.hexsha for c in commit_list]))

        base = self.import_branch + "-base"

        self._set_branch(self.import_branch, self.branch, force=True)
        self.log.info(
            """\
            Creating import branch '%s' from specified commit '%s' in prep to
            linearize the local changes before transposing to the new upstream:
                git branch --force %s %s
            """, self.import_branch, self.branch, self.import_branch,
            self.branch)

        self.log.notice("Attempting to linearise previous changes")
        # attempt to silently linearize the current carried changes as a branch
        # based on the previous located import commit. This provides a sane
        # abort result for if the user needs to abort the rebase of this branch
        # onto the new point upstream that was requested to import from.
        try:
            self._linearise(self.import_branch, strategy,
                            strategy.searcher.commit)
        except:
            # Could ask user if they want to try and use the non clean route
            # provided they don't mind that 'git rebase --abort' will result
            # in a virtually useless local import branch
            self.log.warning(
                """\

                Exception occurred during linearisation of local changes on to
                previous import to simplify behaviour should user need to abort
                the rebase that applies these changes to the latest import
                point. Attempting to tidy up state.

                Do not Ctrl+C unless you wish to need to clean up your git
                repository by hand.

                """)
            # reset head back to the tip of the changes to be rebased
            self._set_branch(self.import_branch, self.branch, force=True)

        rebase = RebaseEditor(interactive, repo=self.repo)
        if len(commit_list):
            first = commit_list[0]

            self.log.info(
                """\
                Rebase changes, dropping merges through editor:
                    git rebase --onto %s \\
                        %s %s
                """, base, first.parents[0].hexsha, self.import_branch)
            status, out, err = rebase.run(commit_list,
                                          first.parents[0].hexsha,
                                          self.import_branch,
                                          onto=base)
            if status:
                if err and err.startswith("Nothing to do"):
                    # cancelled by user
                    self.log.notice("Cancelled by user")
                    return False

                self.log.error("Rebase failed, will need user intervention to "
                               "resolve.")
                if out:
                    self.log.notice(out)
                if err:
                    self.log.notice(err)

                # once we support resuming/finishing add a message here to tell
                # the user to rerun this tool with the appropriate options to
                # complete
                return False

            self.log.notice("Successfully applied all locally carried changes")
        else:
            self.log.warning("Warning, nothing to do: locally carried " +
                             "changes already rebased onto " + self.upstream)
        return True

    def resume(self, args):
        """Resume previous partial import"""
        raise NotImplementedError

    def finish(self):
        """
        Finish merge according to the selected strategy while performing
        suitable verification checks.
        """
        self.log.info("No verification checks enabled")
        self.git.checkout(self.branch)
        current_sha = self.git.rev_parse("HEAD")

        try:
            self.log.info(
                """\
                Merging by inverting the 'ours' strategy discard all changes
                and replace existing branch contents with the new import.
                """)
            self.log.info(
                """\
                Merging import branch to HEAD and ignoring changes:
                    git merge -s ours --no-commit %s
                """, self.import_branch)
            self.git.merge('-s', 'ours', self.import_branch, no_commit=True)
            self.log.info(
                """\
                Replacing tree contents with those from the import branch:
                    git read-tree %s
                """, self.import_branch)
            self.git.read_tree(self.import_branch)
            self.log.info(
                """\
                Committing merge commit:
                    git commit --no-edit
                """)
            self.git.commit(no_edit=True)
            self.log.info(
                """\
                Checking out updated index:
                    git checkout -- .
                """)
            self.git.checkout("--", ".")
            # finally test that everything worked correctly by comparing if
            # the tree object id's match
            if self.git.rev_parse("HEAD^{tree}") != \
                    self.git.rev_parse("%s^{tree}" % self.import_branch):
                raise ImportUpstreamError(
                    "Resulting tree does not match import")
        except (GitCommandError, ImportUpstreamError):
            self.log.error(
                """\
                Failed to finish import by merging branch:
                    '%s'
                into and replacing the contents of:
                    '%s'
                """, self.import_branch, self.branch)
            self._set_branch(self.branch, current_sha, force=True)
            return False
        except:
            self.log.exception("Unknown exception during finish")
            self._set_branch(self.branch, current_sha, force=True)
            raise
        return True


class ImportStrategiesFactory(object):
    __strategies = None

    @classmethod
    def create_strategy(cls, type, *args, **kwargs):
        if type in cls.list_strategies():
            return cls.__strategies[type](*args, **kwargs)
        else:
            raise RuntimeError("No class implements the requested strategy: "
                               "{0}".format(type))

    @classmethod
    def list_strategies(cls):
        cls.__strategies = {
            subclass._strategy: subclass
            for subclass in LocateChangesStrategy.__subclasses__()
            if subclass._strategy}
        return cls.__strategies.keys()


from git_upstream.lib.searchers import (NoMergeCommitFilter,
                                        ReverseCommitFilter,
                                        DiscardDuplicateGerritChangeId,
                                        SupersededCommitFilter,
                                        DroppedCommitFilter)


class LocateChangesStrategy(GitMixin, Sequence):
    """
    Base class that needs to be extended with the specific strategy on how to
    handle changes locally that are not yet upstream.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, git=None, *args, **kwargs):
        """
        Initialize an empty filters list
        """
        self.data = None
        self.filters = []
        super(LocateChangesStrategy, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        if not self.data:
            self.data = self._popdata()
        return self.data[key]

    def __len__(self):
        if not self.data:
            self.data = self._popdata()
        return len(self.data)

    @classmethod
    def get_strategy_name(cls):
        return cls._strategy

    def filtered_iter(self):
        # chain the filters as generators so that we don't need to allocate new
        # lists for each step in the filter chain.
        commit_list = self
        for f in self.filters:
            commit_list = f.filter(commit_list)

        return commit_list

    def filtered_list(self):

        return list(self.filtered_iter())

    def _popdata(self):
        """
        Should return the list of commits from the searcher object
        """
        return self.searcher.list()


class LocateChangesWalk(LocateChangesStrategy):
    """
    """

    _strategy = "drop"

    def __init__(self, branch="HEAD", search_ref=None, *args, **kwargs):
        self.searcher = UpstreamMergeBaseSearcher(branch=branch,
                                                  pattern=search_ref)
        self.search_ref = search_ref
        super(LocateChangesWalk, self).__init__(*args, **kwargs)

    def filtered_iter(self):
        # may wish to make class used to remove duplicate objects configurable
        # through git-upstream specific 'git config' settings
        if self.search_ref:
            self.filters.append(
                DiscardDuplicateGerritChangeId(self.search_ref,
                                               limit=self.searcher.commit))
        self.filters.append(NoMergeCommitFilter())
        self.filters.append(ReverseCommitFilter())
        self.filters.append(DroppedCommitFilter())
        self.filters.append(
            SupersededCommitFilter(self.search_ref,
                                   limit=self.searcher.commit))

        return super(LocateChangesWalk, self).filtered_iter()


@subcommand.arg('-d', '--dry-run', dest='dry_run', action='store_true',
                default=False,
                help='Only print out the list of commits that would be '
                     'applied.')
@subcommand.arg('-i', '--interactive', action='store_true', default=False,
                help='Let the user edit the list of commits before applying.')
@subcommand.arg('-f', '--force', dest='force', required=False,
                action='store_true', default=False,
                help='Force overwrite of existing import branch if it exists.')
@subcommand.arg('--merge', dest='merge', required=False, action='store_true',
                default=True,
                help='Merge the resulting import branch into the target branch'
                     ' once complete')
@subcommand.arg('--no-merge', dest='merge', required=False,
                action='store_false',
                help="Disable merge of the resulting import branch")
@subcommand.arg('-s', '--strategy', metavar='<strategy>',
                choices=ImportStrategiesFactory.list_strategies(),
                default=LocateChangesWalk.get_strategy_name(),
                help='Use the given strategy to re-apply locally carried '
                     'changes to the import branch. (default: %(default)s)')
@subcommand.arg('--into', dest='branch', metavar='<branch>', default='HEAD',
                help='Branch to take changes from, and replace with imported '
                     'branch.')
@subcommand.arg('--import-branch', metavar='<import-branch>',
                help='Name of import branch to use',
                default='import/{describe}')
@subcommand.arg('upstream_branch', metavar='<upstream-branch>', nargs='?',
                default='upstream/master',
                help='Upstream branch to import. Must be specified if '
                     'you wish to provide additional branches.')
@subcommand.arg('branches', metavar='<branches>', nargs='*',
                help='Branches to additionally merge into the import branch '
                     'using default git merging behaviour')
def do_import(args):
    """
    Import code from specified upstream branch.

    Creates an import branch from the specified upstream branch, and optionally
    merges additional branches given as arguments. Current branch, unless
    overridden by the --into option, is used as the target branch from which a
    list of changes to apply onto the new import is constructed based on the
    the specified strategy.

    Once complete it will merge and replace the contents of the target branch
    with those from the import branch, unless --no-merge is specified.
    """

    logger = log.get_logger('%s.%s' % (__name__,
                                       inspect.stack()[0][0].f_code.co_name))

    import_upstream = ImportUpstream(branch=args.branch,
                                     upstream=args.upstream_branch,
                                     import_branch=args.import_branch,
                                     extra_branches=args.branches)

    logger.notice("Searching for previous import")
    strategy = ImportStrategiesFactory.create_strategy(
        args.strategy, branch=args.branch, search_ref=args.upstream_branch)

    if len(strategy) == 0:
        raise ImportUpstreamError("Cannot find previous import")

    # if last commit in the strategy was a merge, then the additional branches
    # that were merged in previously can be extracted based on the commits
    # merged.
    prev_import_merge = strategy[-1]
    if len(prev_import_merge.parents) > 1:
        idx = next((idx for idx, commit in enumerate(prev_import_merge.parents)
                    if commit.hexsha == strategy.searcher.commit.hexsha), None)

        if idx:
            additional_commits = prev_import_merge.parents[idx + 1:]
            if additional_commits and not args.branches:
                logger.warning("""\
                    **************** WARNING ****************
                    Previous import merged additional branches but non have
                    been specified on the command line for this import.\n""")

    if args.dry_run:
        commit_list = [c.hexsha[:6] + " - " + c.summary[:60] +
                       (c.summary[60:] and "...")
                       for c in list(strategy.filtered_iter())]
        logger.notice("""\
            Requested a dry-run: printing the list of commit that should be
            rebased

                %s
            """, "\n    ".join(commit_list))
        return True

    logger.notice("Starting import of upstream")
    import_upstream.create_import(force=args.force)
    logger.notice("Successfully created import branch")

    if not import_upstream.apply(strategy, args.interactive):
        logger.notice("Import cancelled")
        return False

    if not args.merge:
        logger.notice(
            """\
            Import complete, not merging to target branch '%s' as requested.
            """, args.branch)
        return True

    logger.notice("Merging import to requested branch '%s'", args.branch)
    if import_upstream.finish():
        logger.notice(
            """\
            Successfully finished import:
                target branch: '%s'
                upstream branch: '%s'
                import branch: '%s'""", args.branch, args.upstream_branch,
            import_upstream.import_branch)
        if args.branches:
            for branch in args.branches:
                logger.notice("    extra branch: '%s'", branch, dedent=False)


# vim:sw=4:sts=4:ts=4:et:
