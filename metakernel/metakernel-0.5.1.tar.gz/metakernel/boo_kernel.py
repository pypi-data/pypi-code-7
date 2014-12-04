from metakernel import ProcessMetaKernel
from metakernel.process_metakernel import REPLWrapper

class BooKernel(ProcessMetaKernel):
    # Identifiers:
    implementation = 'boo_kernel'
    language = 'boo'

    _banner = None
    @property
    def banner(self):
        if self._banner is None:
            self._banner = "Boo version 0.0"
        return self._banner

    def makeWrapper(self):
        command = 'booish'
        prompt_change = None
        prompt_cmd = "..."
        orig_prompt = ">>>"

        return REPLWrapper(command, orig_prompt, prompt_change,
                           prompt_cmd=prompt_cmd)

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=BooKernel)
