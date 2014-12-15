import sys
from . import pyvcf

def vcf_to_cloudmap (mode, ifile, sample, reference = None, ofile = None, seqdict_file = None, verbose = False):
    mode = mode.upper()
    if mode in ('VARIANT', 'HAWAIIAN'):
        if not reference:
            raise RuntimeError('Mode "{0}" requires reference to be specified.'
                                .format(mode))
    elif mode == "EMS":
        if reference:
            raise RuntimeError('Reference can not be used in mode "{0}"'
                                .format(mode))
    else:
        raise ValueError ('Expected one of "EMS", "VARIANT", "HAWAIIAN" for mode.')
            
    if seqdict_file:
        cloudmap_seqdict_from_vcf (ifile, seqdict_file)
    try:
        vcf = pyvcf.open(ifile)
        if not ofile:
            out = sys.stdout
        else:
            out = open(ofile, 'w')

        if sample not in vcf.info.sample_names:
            raise RuntimeError('Sample {0}: no such sample name in the vcf file.'.format(sample))

        out.write(str(vcf.info.sample_slice([sample])) + '\n')

        if mode == 'EMS':
            for record in vcf:
                out.write(str(record.sample_slice([sample])) + '\n')
        elif mode == 'VARIANT':
            if reference not in vcf.info.sample_names:
                raise RuntimeError('Reference sample {0}: no such sample name in the vcf file.'.format(reference))

            for record in vcf:
                alt_allele_nos = [int(n) for n in record.sampleinfo['GT'][reference].split('/') if n != '0' and n != '.']
                dpr_counts = record.sampleinfo['DPR'][sample].split(',')
                for allele_no in sorted(range(1, len(dpr_counts)), key = lambda index: dpr_counts[index], reverse = True):
                    if allele_no not in alt_allele_nos:
                        break
                record.alt = record.alt_from_num(allele_no)
                record.sampleinfo['AD'] = {}
                record.sampleinfo['AD'][sample] = '{0},{1}'.format(dpr_counts[0], dpr_counts[allele_no])
                record = record.sample_slice([sample])
                out.write(str(record) + '\n')
        elif mode == 'HAWAIIAN':
            if reference not in vcf.info.sample_names:
                raise RuntimeError('Reference sample {0}: no such sample name in the vcf file.'.format(reference))

            for record in vcf:
                alt_allele_nos = [int(n) for n in record.sampleinfo['GT'][reference].split('/') if n != '0' and n !='.']
                if len(set(alt_allele_nos)) == 1:
                    record.alt = record.alt_from_num(alt_allele_nos[0])
                    dpr_counts = record.sampleinfo['DPR'][sample].split(',')
                    record.sampleinfo['AD'] = {}
                    record.sampleinfo['AD'][sample] = '{0},{1}'.format(dpr_counts[0], dpr_counts[alt_allele_nos[0]])
                    record = record.sample_slice([sample])
                    out.write(str(record) + '\n')
        else:
            raise AssertionError('Oh oh, this looks like a bug')
            
    finally:
        try:
            vcf.close()
        except:
            pass
        if out is not sys.stdout:
            try:
                out.close()
            except:
                pass
            
def cloudmap_seqdict_from_vcf (ifile, ofile = None):
    try:
        vcf = pyvcf.open(ifile)
        if not ofile:
            out = sys.stdout
        else:
            out = open(ofile, 'w')
        
        for ident, length in vcf.info.contigs.items():
                out.write ('{0}\t{1}\n'.format(ident, int(length)//10**6+1))
    finally:
        try:
            vcf.close()
        except:
            pass
        if out is not sys.stdout:
            try:
                out.close()
            except:
                pass
    
