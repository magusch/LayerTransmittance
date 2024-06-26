import time

import numpy as np
import plotly.graph_objects as go

from app.layer_transmittance_calculator import LayerTransmittanceCalculator

class LayerParameters:
    def __init__(self, parameters):
        for key, value in parameters.items():
            setattr(self, key, value)
    def __getitem__(self, key):
        return self.__dict__[key]


class TransmittancePlotter:
    def __init__(self, **parameters):
        self.layer_params = LayerParameters(parameters)
        self.output_url = {}
        self.fig = go.Figure()
        self.ylab = {
            'R':'Reflection coefficient',
            'T':'Transmission coefficient',
            'OD':'Optical density'}


    # height - dict for calculation; d – dict with all values of height layers, o – what layer
    # het(d = {1:[40,20,0], 2:[30,0], 3:[50,100]}, height = {0:0},  layer = 1)
    def het(self, d,ri, height={}, o=1):

        for h in d[o]:
            height[o] = float(h)
            if (h == 0) & (o != self.layer_params.amountoflayers):
                height.pop(o)
                ri['n'].pop(o)
                ri['k'].pop(o)
            try:
                x, output = self.het(d,ri, height, o + 1)
            except:
                self.layer_params.height = height
                if self.layer_params.wit == 'angle':
                    x, output = self.calc_on_teta(height, ri)
                else:
                    x, output = self.calc_on_wv(height, ri)
        return x, output

    def calc_on_wv(self, height, ri):
        output, wv = self.plot_transmittance_vs_wavelength(height, ri)
        return wv, output

    def calc_on_teta(self, height, ri):
        angle_inDegree, output = self.plot_transmittance_vs_angle(height, ri)
        return angle_inDegree, output

    def plot_transmittance_vs_wavelength(self, height, ri):
        angle = self.layer_params.angle
        output = {}
        for theta in angle:
            self.layer_params.theta = theta
            layer_transmittance = LayerTransmittanceCalculator(self.layer_params, height, ri)
            output_new, wv = layer_transmittance.calculate_output()
            output[theta] = output_new
            self.label = self.labels_good()
            self.fig.add_trace(go.Scatter(
                x=wv, y=output[theta][self.layer_params.y_label],
                name=self.label, line_shape='linear'
            ))
            self.output_urls(wv, output[theta])
        self.fig.update_layout(xaxis_title='Wavelength, nm')
        return output, wv

    def plot_transmittance_vs_angle(self, height, ri):
        angle = self.layer_params.angle
        self.layer_params.theta = angle

        layer_transmittance = LayerTransmittanceCalculator(self.layer_params, height, ri)
        output, wv = layer_transmittance.calculate_output()

        angle_inDegree = angle * 360 / (2 * np.pi)

        self.label = self.labels_good()
        self.fig.add_trace(go.Scatter(
            x=angle_inDegree, y=output[self.layer_params.y_label],
            name=self.label,line_shape='linear'
        ))
        self.fig.update_layout(xaxis_title='Angle, degree')
        self.output_urls(angle_inDegree, output)
        return angle_inDegree, output

    def output_urls(self, X, output):
        save_file = np.vstack(
            [[self.layer_params.wit, 'R', 'T', 'OD'], np.array([X, output['R'], output['T'], output['OD']]).transpose()])
        filename = str(time.time()) + '.csv'
        csv_path = 'app/static/plot/' + filename

        np.savetxt(csv_path, save_file, delimiter=";", fmt='%s')
        if self.label == '':
            self.label = self.title_to_str()
        self.output_url[self.label] = filename

    def title_to_str(self):  # dict title to string
        title = self.layer_params.title
        str_title = ''
        try:
            str_title += str(title['material'])[1:-1] + '; '
        except:
            pass
        for i, n in title['n'].items():
            if n != None:
                str_title += f"n{i}: {n}; "  # +{k}j
        str_title += '\n'
        for key, item in title.items():
            if (item == None) or (key == 'd') or (key == 'n') or (key == 'material'):
                continue
            str_title += f"{key}: {item}; "
        for i, d in title['d'].items():
            if d != None and d != 0:
                str_title += f"d{i}: {d} nm; "

        return str_title

    def labels_good(self):  # angle, height, n0, n_last
        labels = {}
        aol = self.layer_params.amountoflayers

        for key, d in self.layer_params.title['d'].items():
            if d == None:
                labels['d' + str(key)] = self.layer_params.height[key]
        if self.layer_params.title['n'][aol] == None:
            labels['n_last'] = self.layer_params.n[aol]

        if (self.layer_params.title['angle'] == None) \
                & (self.layer_params.wit != 'angle'):
            labels['angle'] = round(self.layer_params.theta * 360 / (2 * np.pi), 2)

        labels = str(labels)[1:-1]
        return labels

    def run(self):
        aol = self.layer_params.amountoflayers
        n_last = self.layer_params.n[aol]
        d = self.layer_params.d

        for n_aol in n_last:
            self.layer_params.n[aol] = n_aol
            ri = {
                'n': self.layer_params.n,
                'k': self.layer_params.k
            }
            self.het(d, ri)

        self.fig.update_layout(
            title=self.title_to_str(),
            yaxis_title=self.ylab[self.layer_params.y_label]
        )
        return self.fig, self.output_url