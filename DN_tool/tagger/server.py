from collections import OrderedDict
from io import BytesIO
import json
import urllib
import multiprocessing
import PIL.Image
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory, send_file

ADDRESS = 'http://10.22.64.180'


class FlaskServer:
    '''
    A simple Flask server to serve the `Vue.js` based single page application (in `static`).

    Usage:
    ```python
    >>> from lab518_lung.lkds.preprocessing import DataCase
    >>> case1 = DataCase.from_cache('train3')
    >>> server = FlaskServer()
    >>> server.serve(field=case1.name, data=case1.voxel)
    >>> case2 = DataCase.from_cache('test1')
    # roi is a list of dict with the 5 fields
    >>> roi = [{'p': 1,'r': 11.67,'x': 222.20,'y': 258.04,'z': 224.13}]
    >>> server.serve(field=case2.name, data=case2.voxel, roi=roi)
    >>> server.run(port=5005)
    ```
    to reset,
    ```python
    >>> server.reset() # reset can run if and only if after `server.run()`
    ```
    '''

    def __init__(self, serving={}):

        self.serving = OrderedDict(serving)

        app = Flask(__name__)

        @app.route("/")
        def index():
            return app.send_static_file('index.html')

        @app.route('/<field>/<i>')
        def serve_img(field, i):
            data = self.serving[field]['data']
            length = data.shape[0]
            img = PIL.Image.fromarray(data[int(i) % length], "L")
            return serve_pil_image(img)

        @app.route('/static/<path>')
        def get_assets(path):
            return app.send_static_file(path)

        @app.route('/info/')
        def get_field():
            fields = list(self.serving.keys())
            return jsonify({"fields": fields})

        @app.route('/info/<field>')
        def get_info(field):
            rest = self.serving[field]
            depth, height, width = rest['data'].shape
            roi = rest['roi']
            return jsonify({'depth': depth, 'height': height, 'width': width, 'roi': roi})

        @app.route('/rois/<field>/<i>', methods=["GET", 'POST'])
        def change_roi_tag(field, i):
            if request.method == "POST":
                self.serving[field]['roi'][int(i)]['tag'] = request.json['tag']
            return jsonify({"tag": self.serving[field]['roi'][int(i)]['tag']})

        @app.route('/rois/')
        def get_all_rois():
            '''
            ('seriesuid','coordX','coordY','coordZ','probability','tag')
            '''
            ret = []
            for k in self.serving:
                rois = self.serving[k]['roi']
                for roi in rois:
                    ret.append([k, roi['x'], roi['y'], roi['z'],
                                roi['p'], roi['tag']])
            return jsonify({"rois": ret})

        self.app = app

    def serve(self, field, data, roi=[]):
        '''
        roi: list of dict, e.g.
        [
            {"p": 0.9,
            "r": 8,
            "x": 30,
            "y": 50.4,
            "z": 199,
            "tag": "pass"}
        ]
        tag: pass/yes/no
        '''
        self.serving[field] = {'data': data.astype(np.uint8), 'roi': roi}

    def serve_result_file(self, result_file, names=None):
        df = pd.read_csv(result_file)
        map_name_to_roi = Result2Roi(df)
        if names is None:
            names = df['seriesuid'].unique()
        for name in names:
            self.serve(data=Case(name).voxel, field=name,
                       roi=map_name_to_roi(name))

    def pop(self, field=None):
        if field is None:
            self.serving = OrderedDict()
        else:
            self.serving.pop(field)

    def _run(self, port):
        if not self.serving:
            raise ValueError("Serving empty!")
        self.app.run(port=port, host='0.0.0.0')

    def run(self, port=5005):
        self._p = multiprocessing.Process(target=self._run, args=(port,))
        self._p.start()
        print("Running %s:%s (If you're running the utils locally, use `localhost:$port$` instead)."
              % (ADDRESS, port))
        self.pop()
        self.reset = self.__reset
        self.get_results = lambda: self.__get_results(port)

    def __reset(self):
        self._p.terminate()

    def __get_results(self, port):
        url = '{address}:{port}'.format(address=ADDRESS, port=port)
        return get_results_df(url)


def get_results_df(url):
    with urllib.request.urlopen('{url}/rois/'.format(url=url)) as j:
        lst = json.loads(j.read().decode('utf-8'))['rois']
    df = pd.DataFrame(lst, columns=('seriesuid', 'coordX', 'coordY', 'coordZ',
                                    'probability', 'tag'))
    return df


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=100)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


class Result2Roi:
    def __init__(self, df, sort=True):
        self.df = df
        if 'tag' not in self.df.columns:
            self.df['tag'] = 'pass'
        self.sort = sort

    def __call__(self, name):
        name_df = self.df[self.df['seriesuid'] == name]
        ret = []
        for i, row in name_df.iterrows():
            ret.append({"x": row['coordX'], "y": row['coordY'], "z": row['coordZ'],
                        "r": 24, "p": row['probability'], 'tag': row['tag']})
        if self.sort:
            ret = sorted(ret, key=lambda d: -d['p'])
        return ret


def nodule_to_roi(nodule):
    '''
    ```python
    nodule = NODULE_v2[NODULE_v2['name']=='p1']
    ```
    '''
    ret = []
    for i in range(nodule.shape[0]):
        row = nodule.iloc[i]
        ret.append({"x": row['X'], "y": row['Y'],
                    "z": row['Z'], "r": row["r"], "p": 1})
    return ret


if __name__ == '__main__':
    import pandas as pd
    from lab518_lung.dataloader import Case

    map_name_to_roi = Result2Roi(pd.read_csv('/home/jiancheng/code/lung/workspace/'
                                             'jiancheng/sample_result.csv'))
    server = FlaskServer()
    for nid in range(2):
        name = 'newtest' + str(nid + 1)
        server.serve(data=Case(name).voxel, field=name,
                     roi=map_name_to_roi(name))
    server.app.run(port=3003, debug=True, host='0.0.0.0')
