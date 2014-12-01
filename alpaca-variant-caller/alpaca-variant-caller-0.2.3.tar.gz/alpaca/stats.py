

"""
Statistical tests, implemented in OpenCL.
"""


__author__ = "Johannes Köster"
__license__ = "MIT"


import numpy as np
from pyopencl.elementwise import ElementwiseKernel
import pyopencl.array as clarray
from mako.template import Template


class FisherExact:
    preamble = Template(
        r"""
        #define EPSILON 0.0000001f

        inline float hypergeom_prob(const int a, const int b, const int c, const int d, const int n)
        {
            float p = 1;
            int j = n;
            int jmin = b + d;

            for(int i=a+1; i<=a+b; i++)
            {
                p *= i;
                p /= i - a;
                while(p > 1 && j > jmin)
                {
                    p /= j;
                    j--;
                }
            }

            for(int i=c+1; i<=c+a; i++)
            {
                p *= i;
                while(p > 1 && j > jmin)
                {
                    p /= j;
                    j--;
                }
            }

            for(int i=d+1; i<=d+c; i++)
            {
                p *= i;
                while(p > 1 && j > jmin)
                {
                    p /= j;
                    j--;
                }
            }

            while(j > jmin && p > 0)
            {
                p /= j;
                j--;
            }

            return min(p, 1.0f);
        }
        """
    ).render(epsilon=np.finfo(np.float32).eps)

    def __init__(self, cl_context):
        self.cl_hypergem_prob = ElementwiseKernel(cl_context,
            "const int* as,"
            "const int* bs,"
            "const int* cs,"
            "const int* ds,"
            "float* pvals",
            r"""
            int a = as[i];
            int b = bs[i];
            int c = cs[i];
            int d = ds[i];

            const int n = a + b + c + d;

            const float prob = hypergeom_prob(a, b, c, d, n);

            // calculate the maximum possible a such that b and c don't become negative
            const int maximum_a = a + min(min(a, b), c);
            // calculate the table with minimum a
            const int minimize_a = min(a, d);
            a -= minimize_a;
            b += minimize_a;
            c += minimize_a;
            d -= minimize_a;

            // the probability for the table with minimum a
            float p = hypergeom_prob(a, b, c, d, n);
            // the p-value
            float pval = 0;
            // calculate the p-value by iteratively increasing a and updating the probability
            while(a <= maximum_a)
            {
                // update pval if p is smaller than the prob of the true table
                pval += (p <= prob) * p;

                // update probability
                //const float factor = ((float)b * c) / ((a + 1) * (d + 1));
                p *= b * c;
                p /= ((a + 1) * (d + 1));
                //p *= factor;

                a++;
                b--;
                c--;
                d++;
            }
            pvals[i] = min(1.0f, pval);
            """,
            preamble=self.preamble,
            name="fisher_exact")

    def test(self, cl_a, cl_b, cl_c, cl_d, cl_pval):
        """Calculcate fishers exact two-sided test obtaining a p-value for each contingency table in the array.

        The code implements section 5.2 of Microsoft Technical Report MSR-TR-2009-53, http://research.microsoft.com/apps/pubs/?id=80571 and a variant of section 5.1 that can be found here:
        http://mscompbio.codeplex.com/SourceControl/latest#FalseDiscoveryRate/FalseDiscoveryRateClasses/HypergeometricProbability.cs
        The original code is licensed under the Ms-RL.
        A the definition given there is incorrect, fixes are marked in the code.

        Args:
            cl_a (pyopencl.array.Array): a values of 2x2 contingency tables of dtype np.int32
            cl_b (pyopencl.array.Array): b values of 2x2 contingency tables of dtype np.int32
            cl_c (pyopencl.array.Array): c values of 2x2 contingency tables of dtype np.int32
            cl_d (pyopencl.array.Array): d values of 2x2 contingency tables of dtype np.int32
            cl_pval (pyopencl.array.Array): the np.float32 array the p-values will be stored in
        """
        self.cl_hypergem_prob(cl_a, cl_b, cl_c, cl_d, cl_pval)
