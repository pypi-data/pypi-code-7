# encoding: utf-8
import os
import sys
import yaml
from edopkg import pyaml

OBJ_CATS = ['workflow', 'mdset', 'rule', 'script', 'template',
        'stage','skin', 'resource', 'form']

class EdoPackage:

    def __init__(self, wo_client, local_root):
        self.remote_pkg = wo_client.package
        self.local_root = local_root
        self.pkg_name = os.path.basename(local_root)

    def pull(self, path_filter=''):
        sys.stdout.write('\rpulling...')
        if not path_filter or path_filter == 'config.yaml':
            pkg_info = self.remote_pkg.get(self.pkg_name, detail=False)
            self.write_yaml('config.yaml', pkg_info)

        # 写入软件包对象
        for obj_cat in OBJ_CATS:
            obj_folder = obj_cat + 's'

            # 过滤
            if path_filter and not path_filter.startswith(obj_folder):
                continue

            # 计算文件的过滤条件
            filename_filter = path_filter[len(obj_folder) + 1:] if path_filter else ''

            # 逐个对象同步
            for obj_name in getattr(self.remote_pkg, 'list_' + obj_folder)(self.pkg_name):
                self.pull_obj(obj_cat, obj_name, obj_folder, filename_filter)

        print '\rpull successful'.ljust(60)

    def push(self, path_filter=''):
        sys.stdout.write('\rpushing...')

        if not path_filter or path_filter == 'config.yaml':
            pkg_info = self.read_yaml('config.yaml')
            pkg_list = self.remote_pkg.list()
            if self.pkg_name not in pkg_list:
                status = self.remote_pkg.new(self.pkg_name, pkg_info)
            status = self.remote_pkg.set(self.pkg_name, pkg_info)

        # 读取软件包对象
        for obj_cat in OBJ_CATS:
            filename_filter = ''
            obj_folder = obj_cat + 's'
            # 过滤
            if path_filter:
                if not path_filter.startswith(obj_folder):
                    continue
                else: filename_filter = path_filter[len(obj_folder) + 1:]

            # 判断是否存在文件夹
            cat_path = os.path.join(self.local_root, obj_folder)
            if not os.path.exists(cat_path):
                continue

            # 逐个上传
            for obj_filename in os.listdir(cat_path):
                # 过滤
                if filename_filter and not obj_filename.startswith(filename_filter):
                    continue

                # TODO: 资源文件夹迭代push

                #  同步
                self.push_obj(obj_cat, obj_folder, obj_filename)

        print '\rpush successful'.ljust(60)

    def pull_obj(self, obj_cat, obj_name, obj_folder, filename_filter):
        # 读取文件名
        if obj_cat == 'resource':
            obj_filename = os.path.normpath(obj_name)
        elif obj_cat == 'template':
           obj_filename = obj_name.split(':')[1] + '.pt'
        else:
           obj_filename = obj_name.split(':')[1] + '.yaml'

        # 过滤
        if filename_filter and not obj_filename.startswith(filename_filter):
            return

        # 更新提示
        sys.stdout.write('\rpulling ' + obj_name.ljust(60))

        # 下载数据
        if obj_cat == 'resource':
            obj_data = self.remote_pkg.get_resource(self.pkg_name, path = obj_name).text
        else:
            obj_data = getattr(self.remote_pkg, 'get_' + obj_cat)(obj_name)

        # 写入数据
        obj_path = os.path.join(obj_folder, obj_filename)

        # 判断文件是否已经存在
        dirname = os.path.dirname(obj_path)
        if not os.path.exists( dirname):
            os.makedirs(dirname)

        if obj_cat == 'template':
            self.write_file(obj_path, obj_data['template'])
        elif obj_cat == 'resource':
            self.write_file(obj_path, obj_data)
        else:
            self.write_yaml(obj_path, obj_data)

    def push_obj(self, obj_cat, obj_folder, obj_filename):
        # 更新提示
        sys.stdout.write('\rpushing ' + obj_filename.ljust(60))

        obj_name = obj_filename.split('.')[0]
        # 读取数据
        obj_path = os.path.join(obj_folder, obj_filename)
        if obj_cat == 'template':
            obj_data = self.read_template(obj_name, obj_path)
        elif obj_cat == 'resource':
            obj_stream = self.read_stream(obj_path)
        else:
            obj_data = self.read_yaml(obj_path)

        # 上传数据
        if obj_cat == 'template':
            status = getattr(self.remote_pkg, 'register_' + obj_cat)(
                self.pkg_name, obj_data, overwrite = True)
        elif obj_cat == 'resource':
            status = self.remote_pkg.add_resource(
                self.pkg_name, obj_filename, obj_stream, overwrite=True)
        else:
            status = getattr(self.remote_pkg, 'register_' + obj_cat)(
                self.pkg_name, obj_data, overwrite = True)

    def write_yaml(self, path, data):
        open(os.path.join(self.local_root, path), 'wb').write(pyaml.dump(data))

    def write_file(self, path, data):
        open(os.path.join(self.local_root, path), 'wb').write(data)

    def read_yaml(self, path):
        return yaml.load(open(os.path.join(self.local_root, path)).read())

    def read_template(self, obj_name, path):
        data = open(os.path.join(self.local_root, path)).read()
        return {'name':obj_name, 'title':obj_name, 'template':data}

    def read_stream(self, path):
        return open(os.path.join(self.local_root, path))



