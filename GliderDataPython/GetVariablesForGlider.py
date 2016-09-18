''' This file reads in the variables that we want to store and stores them out to another Mat-file which we might find easier to work with. '''
import scipy.io as sio
import shelve

def GetVariablesAndTranslations(data):
    ''' The locations of the data are so convoluted that we are going to write a function to reach them. '''
    Variables = []
    Translations = []
    
    varIndx = len(data['var'][0][0][0])
    
    for i in range(0,varIndx):
        var_name = data['var'][0][0][0][i][0][0]
        var_indx = data['var'][0][0][0][i][1][0][0]
        Variables.append((var_name,var_indx))
        
    transIndx = len(data['var'][0][0][1])
    for j in range(0,transIndx):
        trans_var_name = data['var'][0][0][1][j][0][0]
        var_name = data['var'][0][0][1][j][1][0]
        Translations.append((trans_var_name,var_name))
    
    return Variables, Translations



gliderVarsDirectory = 'GliderVariables/'

Hehape = sio.loadmat(gliderVarsDirectory+'Hehape_var.mat')
hehape = shelve.open('Hehape_vars.shelf')
hehape['Variables'], hehape['Translations'] = GetVariablesAndTranslations(Hehape)
hehape.close()

Rusalka = sio.loadmat(gliderVarsDirectory+'Rusalka_var.mat')
rusalka = shelve.open('Rusalka_vars.shelf')
rusalka['Variables'],rusalka['Translations'] = GetVariablesAndTranslations(Rusalka)
rusalka.close()
