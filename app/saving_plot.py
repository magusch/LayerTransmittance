import numpy as np
import matplotlib.pyplot as plt

import time

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
        self.ylab = {'R':'Коэффициент отражения', 'T':'Коэффициент пропускания', 'OD':'Оптическая плотность'}


    # height - dict for calculation; d – dict with all values of height layers, o – what layer
    # het(d = {1:[40,20,0], 2:[30,0], 3:[50,100]}, height = {0:0},  layer = 1)
    def het(self, d, height={}, o=1):

        for h in d[o]:
            height[o] = float(h)
            if (h == 0) & (o != self.layer_params.amountoflayers):
                height.pop(o)
                self.layer_params.n.pop(o)
                self.layer_params.k.pop(o)
            try:
                wv, output = self.het(d, height, o + 1)
            except:
                self.layer_params.height = height
                if self.layer_params.wit == 'angle':
                    wv, output = self.calc_on_teta()
                else:
                    wv, output = self.calc_on_wv()
        return (wv, output)

    def calc_on_wv(self):
        output, wv = self.plot_transmittance_vs_wavelength()
        self.output_urls(wv, output[self.layer_params.angle[0]])
        return wv, self.output_url

    def calc_on_teta(self):
        output, angle_inDegree = self.plot_transmittance_vs_angle()
        self.output_urls(angle_inDegree, output)
        return angle_inDegree, self.output_url

    def plot_transmittance_vs_wavelength(self):
        angle = self.layer_params.angle
        output = {}
        for theta in angle:
            self.layer_params.theta = theta
            layer_transmittance = LayerTransmittanceCalculator(self.layer_params)
            output_new, wv = layer_transmittance.calculate_output()
            output[theta] = output_new
            self.label = self.labels_good()
            plt.plot(wv, output[theta][self.layer_params.y_label], label=self.label)
            plt.xlabel('Длина Волны, нм')
        return output, wv

    def plot_transmittance_vs_angle(self):
        angle = self.layer_params.angle
        self.layer_params.theta = angle
        layer_transmittance = LayerTransmittanceCalculator(self.layer_params)
        output, wv = layer_transmittance.calculate_output()

        angle_inDegree = angle * 360 / (2 * np.pi)
        #for theta in angle:
        #self.layer_params.theta = theta
        self.label = self.labels_good()
        plt.plot(angle_inDegree, output[self.layer_params.y_label], label=self.label)
        plt.xlabel('Угол, градусы')
        return output, angle_inDegree

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
        labels = {}  # str??
        aol = self.layer_params.amountoflayers

        for key, d in self.layer_params.d.items():
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
        global output_url
        output_url = {}
        aol = self.layer_params.amountoflayers
        n_last = self.layer_params.n[aol]
        d = self.layer_params.d
        for n_aol in n_last:
            self.layer_params.n[aol] = n_aol
            wv, output = self.het(d)

        plt.ylabel(self.ylab[self.layer_params.y_label])
        # str_title = title_to_str(parametrs['title'])
        # plt.title(str_title)
        plt.legend()  # title = parametrs['title']
        filename_plot = str(int(time.time())) + '.png'
        image_path = 'app/static/plot/' + filename_plot
        plt.savefig(image_path)

        plt.clf()  # delete plot
        return (wv, output, filename_plot)
