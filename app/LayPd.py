import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import time
#from io import BytesIO

pi = np.pi
j = 1j
ylab = {'R':'Коэффициент отражения', 'T':'Коэффициент пропускания', 'OD':'Оптическая плотность'}
output_url = {}

import matplotlib
matplotlib.use('agg')


def Propusk(parametrs,d,teta):
    wv = parametrs['wv']
    n,k = parametrs['n'],parametrs['k']
    amountoflayers = parametrs['amountoflayers']
    #print(parametrs)
    r,t,be = {},{},{}


    M = np.array([[1,0],[0,1]])

    keys = list(n.keys())
    keys.sort()
    io = 0 #zero layer

    matr_delta = {io:np.array([[1,0],[0,1]])}
    eps = {io:n[io]**2}

    kx = np.sqrt(eps[io])*np.sin(teta)
    kz = {io:np.array((2*pi/wv)*np.sqrt(eps[io]-kx**2))}

    for i in keys[1:]:
        try:
            eps[i] = np.array((n[i]+j*k[i])**2, dtype = np.complex)
        except Exception as e:
            print(e)
            eps[i] = np.array((n[i])**2, dtype = np.complex)

        kz[i] = ((2*pi/wv)*np.sqrt(eps[i]-kx**2))

        try:
            be[i] = kz[i]*d[i]
        except:
            be[i] = np.inf

        #______________
        if parametrs['polarization']=='S': # S-polarization
            t[i] = 2*kz[io]/(kz[io]+kz[i]) #S-поляризация
            r[i] = (kz[io]-kz[i])/(kz[io]+kz[i])
        else: 							  # P-polarization
            t[i] = 2*kz[io]*np.sqrt(eps[io]*eps[i])/(eps[i]*kz[io]+eps[io]*kz[i])
            r[i] = (eps[i]*kz[io]-eps[io]*kz[i])/(eps[i]*kz[io]+eps[io]*kz[i])

        matr = np.array([[np.array(1/t[i]), np.array(r[i]/t[i])],[np.array(r[i]/t[i]), 0]])
        matr[1][1] = 1/t[i]	#to make matrix 2x2 with another matrix
        M = np.dot(M,np.dot(matr_delta[io],matr))

        matr_delta[i] = np.array([[np.exp(-j*be[i]), 0],[0, np.exp(j*be[i])]])
        io = i #save index of this layer for next calculation (it is because we use dict with deleting empty layer)


    M = M.dot(np.array([[1],[0]]))


    Reflection = abs(M[1][0]/M[0][0])**2

    Transmission = (1/M[0][0])
    Trans = np.real((kz[amountoflayers]/kz[0])*abs(Transmission)**2)
    if np.min(Trans) != 0: #TODO: исправить если Trans = 0 в одном месте
        OD  =  np.log10(1/Trans)
    else:
        OD = Trans*0
    output = {'R': Reflection, 'T': Trans, 'OD': OD}


    return output, wv



def het(d, parametrs, height = {}, o = 1):  #height - dict for calculation; d – dict with all values of height layers, o – what layer
    #het(d = {1:[40,20,0], 2:[30,0], 3:[50,100]}, height = {0:0},  layer = 1)
    for h in d[o]:
        height[o]  =  int(h)
        if (h==0) & (o !=  parametrs['amountoflayers']):
            height.pop(o)
            parametrs['n'].pop(o)
            parametrs['k'].pop(o)
        try:
            wv,output = het(d,parametrs, height, o+1)
        except:
            if parametrs['wit']=='angle':
                wv,output = calc_on_teta(height, **parametrs)
            else:
                wv,output = calc_on_wv(height, **parametrs)
    return(wv,output)



def calc_on_wv(height, **parametrs): #dependecy of wv with loop for list of angle
    angle = parametrs['angle']
    title = parametrs['title']
    for teta in angle:
        output, wv =  Propusk(parametrs,height,teta)
        labl = labels_good(title,parametrs, height, teta)

        # save_file = np.vstack([['wv', 'R', 'T'], np.array([wv,output['R'],output['T']]).transpose()])

        # filename = str(time.time()) +'.csv'
        # csv_path = 'app/static/plot/'+filename

        # np.savetxt(csv_path, save_file, delimiter = ";",fmt = '%s')

        plt.plot(wv,output[parametrs['y_label']], label = labl)
        plt.xlabel('Длина Волны, нм')

        output_url.update(output_urls(parametrs, wv, output, labl))

    return(wv,output_url)


def calc_on_teta(height, **parametrs): #dependecy of angle
    angle = parametrs['angle']
    title = parametrs['title']
    labl = labels_good(title, parametrs, height, angle)

    output, wv = Propusk(parametrs,height,angle)
    angle_inDegree = angle*360/(2*pi)

    plt.plot(angle_inDegree, output[parametrs['y_label']], label=labl) #(angle*360/(2*pi))
    plt.xlabel('Угол, градусы')

    output_url.update(output_urls(parametrs, angle_inDegree, output,labl))

    return wv, output_url


def output_urls(parametrs, X, output,labl):
    save_file = np.vstack([[parametrs['wit'], 'R', 'T', 'OD'], np.array([X,output['R'],output['T'],output['OD']]).transpose()])

    filename = str(time.time()) +'.csv'
    csv_path = 'app/static/plot/'+filename

    np.savetxt(csv_path, save_file, delimiter = ";", fmt = '%s')
    if labl == '':
        labl = title2str(parametrs['title'])
    output_url[labl]=filename
    return output_url


def labels_good(title,parametrs, height, teta): #angle, height, n0, n_last
    labels = {} #str??
    aol = parametrs['amountoflayers']

    for key, d in title['d'].items():
        if d == None:
            labels['d'+str(key)]=height[key]
    if title['n'][aol] == None:
        labels['n_last'] = parametrs['n'][aol]

    if (title['angle']==None) & (parametrs['wit'] != 'angle'):
        labels['angle'] = round(teta*360/(2*pi),2)

    labels = str(labels)[1:-1]
    return(labels)



def title2str(title): #dict title to string
    str_title = ''
    try:
        str_title += str(title['material'])[1:-1]+'; '
    except:
        pass
    for i,n in title['n'].items():
        if n != None:
            str_title += f"n{i}: {n}; " #+{k}j
    str_title += '\n'
    for key, item in title.items():
        if (item==None) or (key=='d') or (key=='n') or (key=='material'):
            continue
        str_title += f"{key}: {item}; "
    for i, d in title['d'].items():
        if d != None and d!=0:
            str_title += f"d{i}: {d} nm; "

    return str_title


def calculation(parametrs):
    global output_url
    output_url = {}
    aol = parametrs['amountoflayers']
    n_last = parametrs['n'][aol]
    d = parametrs['d']
    for n_aol in n_last:
        parametrs['n'][aol] = n_aol
        wv,output = het(d,parametrs)

    plt.ylabel(ylab[parametrs['y_label']])
    str_title = title2str(parametrs['title'])
    plt.title(str_title)
    plt.legend( ) #title = parametrs['title']
    filename_plot = str(int(time.time())) +'.png'
    image_path = 'app/static/plot/'+filename_plot
    plt.savefig(image_path)


    plt.clf() #delete plot
    return(wv,output,filename_plot)
#plt.show()

# figfile  =  BytesIO() #save in byte, not in file
# plt.savefig(figfile, format = 'png')
# figfile.seek(0)  # rewind to beginning of file
# figdata_png  =  figfile.getvalue()
# image_path  =  base64.b64encode(figdata_png)


# if __name__ == '__main__':
# 	dts = [datas('Al')]#,]
# 	aol = len(dts)+1
# 	aol = 3
# 	wv,n,k = interpolate(dts)

# 	angle = np.arange(1.3,1.57,0.03)
# 	d = {1:[10], 2:[10,20],3:[0]}

# 	n[0],n[aol] = 2.3,[1]
# 	k[0],k[aol] = 0,0

# 	labels = {}


# 	parametrs['d'] = d
# 	#parametrs = {'wv':wv, 'n':n, 'k':k, 'd':d, 'angle':angle,  'amountoflayers':aol, 'y':'R', 'labels':{}}
# 	parametrs['title'] = titles(**parametrs)

# 	for n_aol in n[aol]:
# 		parametrs['n'][aol] = n_aol
# 		het(d,parametrs)
# 	plt.ylabel(ylab[parametrs['y_label']])
# 	plt.title(parametrs['title'])
# 	plt.legend()
# 	plt.show()




