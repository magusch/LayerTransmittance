import numpy as np

class SearchingPlasmonPlace:
    def __init__(self, parameters):
        self.parameters = parameters
        self.pi = np.pi
        self.j = 1j

    def imag_real(self, d_met):
        wv = float(self.parameters['wv'])
        n = [self.parameters['n0'], self.parameters['n1'], self.parameters['n2']]
        n = [float(i) for i in n]
        k = float(self.parameters['k1'])
        k2 = 0
        theta = self.parameters['theta']

        eps_g = n[0] ** 2
        eps_met = np.array((n[1] + self.j * k) ** 2, dtype=np.complex)
        eps_de1 = np.array((n[2] + self.j * k2) ** 2, dtype=np.complex)

        sin = np.array(np.sin(theta), dtype=np.complex)
        kx = np.sqrt(eps_g) * sin
        kz = [np.array((2 * self.pi / wv) * np.sqrt(eps_g - kx ** 2))]
        kz.append((2 * self.pi / wv) * np.sqrt(eps_met - kx ** 2))
        kz.append((2 * self.pi / wv) * np.sqrt(eps_de1 - kx ** 2))

        r = []
        r.append((eps_met * kz[0] - eps_g * kz[1]) / (eps_met * kz[0] + eps_g * kz[1]))
        r.append((eps_de1 * kz[1] - eps_met * kz[2]) / (eps_de1 * kz[1] + eps_met * kz[2]))

        sin_theta = np.sqrt((eps_met * eps_de1) / (eps_met + eps_de1)).real / n[0]

        d_min = 0
        theta_min = 0

        # min_z = 0.02
        min_z = abs(d_met[1] - d_met[0]) / 2

        for d in d_met:
            r012_chisl = r[0] + r[1] * np.exp(self.j * 2 * kz[1] * d)
            x = r012_chisl.real
            y = r012_chisl.imag

            zero_array = np.sqrt(x ** 2 + y ** 2)
            min_z_index = list(zero_array).index(zero_array.min())
            if zero_array[min_z_index] < min_z:
                min_z = zero_array[min_z_index]
                d_min = d
                theta_min = self.parameters['theta'][min_z_index]

        return d_min, theta_min

    def find_d_met(self):
        self.parameters['theta'] = np.arange(0, 1.57, 0.00001)

        d_range_dict = {'d_range_min': 5, 'd_range_max': 100, 'd_range_step': 5}

        while d_range_dict['d_range_step'] > 0.001:
            d_range = np.arange(d_range_dict['d_range_min'], d_range_dict['d_range_max'], d_range_dict['d_range_step'])
            d_met_new, theta_min_new = self.imag_real(d_range)

            if d_met_new == 0: break
            d_met, theta_min = d_met_new, theta_min_new

            if d_met != 0:
                d_met_i = list(d_range).index(d_met)
            else:
                break

            if d_met_i != 0:
                d_range_dict['d_range_min'] = d_range[d_met_i - 1]
            else:
                d_range_dict['d_range_min'] = d_range[d_met_i] - d_range_dict['d_range_step'] / 10

            if d_met_i != list(d_range).index(d_range[-1]):
                d_range_dict['d_range_max'] = d_range[d_met_i + 1]
            else:
                d_range_dict['d_range_max'] = d_range[d_met_i] + d_range_dict['d_range_step'] / 10

            d_range_dict['d_range_step'] = (d_range_dict['d_range_max'] - d_range_dict['d_range_min']) / 10

        return (d_met, theta_min)

