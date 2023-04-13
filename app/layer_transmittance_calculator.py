import numpy as np

class LayerTransmittanceCalculator:

    def __init__(self, parameters, height, ri):
        self.parameters = parameters
        self.wv = parameters['wv']
        self.n = ri['n']
        self.k = ri['k']
        self.theta = parameters['theta']
        self.d = height # parameters['d']
        self.amountoflayers = parameters['amountoflayers']
        self.M = np.array([[1, 0], [0, 1]])

        self.pi = np.pi
        self.j = 1j
        self.ylab = {
            'R': 'Коэффициент отражения',
            'T': 'Коэффициент пропускания',
            'OD': 'Оптическая плотность'
        }


    def _get_eps(self, i):
        try:
            eps = np.array((self.n[i] + 1j * self.k[i]) ** 2, dtype=np.complex)
        except Exception as e:
            print(e)
            eps = np.array((self.n[i]) ** 2, dtype=np.complex)
        return eps

    def _get_kz(self, i, kx):
        eps_i = self._get_eps(i)
        kz_i = ((2 * np.pi / self.wv) * np.sqrt(eps_i - kx ** 2))
        return kz_i

    def _calculate_matrices(self):
        r,t,be = {},{},{}

        io = 0 # zero layer
        matr_delta = {
            io: np.array([[1,0],[0,1]])
        }
        eps = {
            io: self._get_eps(io)
        }
        kx = np.sqrt(eps[io])*np.sin(self.theta)

        kz = {
            io: self._get_kz(io, kx)
        }

        keys = list(self.n.keys())
        keys.sort()
        for i in keys[1:]:
            eps[i] = self._get_eps(i)
            kz[i] = self._get_kz(i, kx)
            try:
                be[i] = kz[i]*self.d[i]
            except:
                be[i] = np.inf

            if self.parameters['polarization']=='S': # S-polarization
                t[i] = 2*kz[io]/(kz[io]+kz[i])
                r[i] = (kz[io]-kz[i])/(kz[io]+kz[i])
            else: # P-polarization
                t[i] = 2*kz[io]*np.sqrt(eps[io]*eps[i])/(eps[i]*kz[io]+eps[io]*kz[i])
                r[i] = (eps[i]*kz[io]-eps[io]*kz[i])/(eps[i]*kz[io]+eps[io]*kz[i])

            matr = np.array([
                [ np.array(1/t[i]),     np.array(r[i]/t[i]) ],
                [ np.array(r[i]/t[i]),  0                   ]])
            matr[1][1] = 1/t[i]
            self.M = np.dot(self.M, np.dot(matr_delta[io], matr))

            matr_delta[i] = np.array([
                    [ np.exp(-1j*be[i]),  0                ],
                    [ 0,                  np.exp(1j*be[i]) ]
            ])
            io = i

        return self.M, kz

    def calculate_output(self):
        M, kz = self._calculate_matrices()
        M = M.dot(np.array([[1], [0]]))
        Reflection = abs(M[1][0] / M[0][0]) ** 2
        Transmission = (1 / M[0][0])
        Trans = np.real( (kz[self.amountoflayers] / kz[0]) * abs(Transmission) ** 2)
        if np.min(Trans) != 0:
            OD = np.log10(1/Trans)
        else:
            OD = Trans * 0
        output = {'R': Reflection, 'T': Trans, 'OD': OD}
        return output, self.wv