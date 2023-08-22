# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 16:13:54 2022

@author: ryanbadman
"""

import requests
import re
import urllib3 # import urlopen
from bs4 import BeautifulSoup
# from pattern.web import URL, DOM
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
import requests
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select

import random
import numpy as np


def GenerateNewGlycans(numGlycans = 50, MaxLength = 15, OnlyLinear = False, AllowXyl = True):
    # function body 
    
    seed0 = 15
    random.seed(seed0)
    '''
    numGlycans = 1000 #total number of glycans to simulate
    MaxLength = 15 #lengths will be between 2 and Maxlength long
    OnlyLinear = False # whether to do only linear glycans or branched (currently simple branched only, max 1 branched monosaccharide residue per monosaccharide)
    AllowXyl = True #whether or not to allow Xylose (the only 5 C ring right now)
    '''

    MonosacNames = [] # possible Monosaccharides
    MonosacNamesSpecial = [] # possible Monosaccharides, sulfur ones right now
    Linkages = [] #possible linkages
    GlycanList = [] # final list of GLycans

    Linkages.append('(1-2)')
    Linkages.append('(1-3)')
    Linkages.append('(1-4)')
    Linkages.append('(1-5)')
    Linkages.append('(1-6)')
    Linkages.append('(2-3)')
    Linkages.append('(2-6)')

    MonosacNames.append('aDXylp') # 0 # has no C6, don't use (1-6) or (2-6) # 0
    MonosacNames.append('bDXylp') # 1 # has no C6, don't use (1-6) or (2-6)
    MonosacNames.append('aDGalp') # 2
    MonosacNames.append('bDGalp') # 3
    MonosacNames.append('aDGalpA') # 4
    MonosacNames.append('bDGalpA') # 5
    MonosacNames.append('aDGlcp') # 6
    MonosacNames.append('bDGlcp') # 7
    MonosacNames.append('aDGlcpA') # 8
    MonosacNames.append('bDGlcpA') # 9
    MonosacNames.append('aDFucp') # 10
    MonosacNames.append('bDFucp') # 11
    MonosacNames.append('aLFucp') # 12
    MonosacNames.append('bLFucp') # 13
    MonosacNames.append('aDManp') # 14
    MonosacNames.append('bDManp') # 15
    MonosacNames.append('aDManpA') # 16
    MonosacNames.append('bDManpA') # 17
    MonosacNames.append('[Ac(1-2)]aDGlcpN') # a-D-GlcNAc # 18
    MonosacNames.append('[Ac(1-2)]bDGlcpN') # b-D-GlcNAc # 19
    MonosacNames.append('[Ac(1-5)]aXNeup') # a-D-Neu5Ac # 20
    MonosacNames.append('[Ac(1-5)]bXNeup') # b-D-Neu5Ac # 21

    MonosacNamesSpecial.append('[S-6)]aDGalp')
    MonosacNamesSpecial.append('[S-6)]bDGalp')
    MonosacNamesSpecial.append('[Ac(1-2),S-6)]aDGlcpN')
    MonosacNamesSpecial.append('[Ac(1-2),S-6)]bDGlcpN')
    MonosacNamesSpecial.append('[S-6)]aDGlcp')
    MonosacNamesSpecial.append('[S-6)]bDGlcp')
    MonosacNamesSpecial.append('[S-3)]aDGalp')
    MonosacNamesSpecial.append('[S-3)]bDGalp')

    ######### known errors to NOTE (most are corrected, document if more show up):
        
    # incompatible positions linked: bDFucp C1 and bDGlcp C5
    # Integrity warning: aldose "bDGalp" forms an outgoing bond at position 2 (not at C1)
    # Integrity warning: aldose "bDGlcpA" forms an outgoing bond at position 2 (not at C1)
    # Integrity warning: aldose "aLFucp" forms an outgoing bond at position 2 (not at C1)
    # Integrity warning: ketose "bXNeup" forms an outgoing bond at position 1 (not at C2)
    #Parsing warning: amine (but not alkylamine) bond detected between bDGlcpN and bDGalp. Please check functionalization and substitution positions.
    #Integrity warning: aldose "bDGlcpN" forms an outgoing bond at position 2 (not at C1)
    #Integrity warning: amino-bearing position 2 is substituted by non-alkyls more than once in bDGlcpN
    #Integrity warning: aldose "bDGalpA" forms an outgoing bond at position 2 (not at C1)
    #Integrity warning: aldose "aDFucp" forms an outgoing bond at position 2 (not at C1)
    #Integrity warning: aldose "aLFucp" forms an outgoing bond at position 2 (not at C1)
    # incompatible positions linked: bDGlcpA C1 and bXNeup C3
    # incompatible positions linked: aXNeup C2 and bXNeup C3
    #hydroxy-bearing position 3 is substituted more than once in bDGalp
    # Fatal error: Could not parse structure aDXylp(1-3)[Ac(1-5)]aXNeup(2-3)bLFucp(1-2)[S-6)]aDGlcp(1-4)bDGlcpA(1-3)[aDXylp(1-4)]bDFucp(1-4)bLFucp(1-3)[bDXylp(1-2)]bDManp(1-3)bDManp
    #Parsing error: incompatible positions linked: aDXylp C1 and aXNeup C3. Please check deoxygenation and substitution positions. For C-linkage use a special marker.


    # Fatal error: Could not parse structure bDGalp(1-3)[Ac(1-2)]aDGlcpN(1-5)[S-6)]bDGlcp(1-2)[Ac(1-2)]aDGlcpN
    #Parsing warning: amine (but not alkylamine) bond detected between bDGlcp and aDGlcpN. Please check functionalization and substitution positions.
    #Parsing error: incompatible positions linked: aDGlcpN C1 and bDGlcp C5. Please check deoxygenation and substitution positions. For C-linkage use a special marker.

    # Fatal error: Could not parse structure aDXylp(1-3)aDFucp(1-2)aLFucp(1-4)aDGlcp(1-4)aDGlcp(1-6)aLFucp(1-4)aDGlcp(1-6)aDGalp
    #Parsing error: incompatible positions linked: aDGlcp C1 and aLFucp C6. Please check deoxygenation and substitution positions. For C-linkage use a special marker.


    #for i in range(numGlycans):
    i = 0
    while i <= numGlycans:
        i = len(GlycanList)    
        currentLength = 0
        GlycanLength = np.random.randint(2,MaxLength,1)
        print('Glycan Length: ', GlycanLength)
        
        ##################################################
            
        if OnlyLinear == False:
            if AllowXyl == True:
                
                nLink = np.random.randint(0,len(Linkages)-4,(GlycanLength[0]-1)) # to do just 1-2, 1-3, 1-4
                nMono = np.random.randint(0,len(MonosacNames),(GlycanLength[0]))
                
                GlycanName = ''
                lastLinkage = ''
                lastMono = ''
                j = 0
                currentLength = 0
                while j < (GlycanLength[0]-1):
                    j = currentLength
                    #j  = currentLength
                    print ('j ', j, 'length ', GlycanLength)
                    #print(j)
                    
                    if currentLength == 0:
                        GlycanName = str(MonosacNames[nMono[j]]) + GlycanName
                        currentLength = currentLength + 1
                        
                    if currentLength > 0: # and j < (GlycanLength - 1): 
                        if currentLength < (GlycanLength[0]-1):      
                            
                            specialRand = random.uniform(0, 1)
                            
                            if specialRand < 0.15:
                            
                                nMonoSpecial = np.random.randint(0,len(MonosacNamesSpecial),1)
                                specialRandlink = random.uniform(0, 1)
                                
                                if specialRandlink > 0.5:
                                    if currentLength < (GlycanLength[0]-1):
                                       GlycanName = str(MonosacNamesSpecial[nMonoSpecial[0]]) + '(1-2)' + GlycanName
                                       lastLinkage = '(1-2)' 
                                       lastMono = MonosacNamesSpecial[nMonoSpecial[0]]
                                       currentLength = currentLength + 1
                                    
                                if specialRandlink <= 0.5:
                                    if currentLength < (GlycanLength[0]-1):
                                        GlycanName = str(MonosacNamesSpecial[nMonoSpecial[0]]) + '(1-4)' + GlycanName   
                                        lastLinkage = '(1-4)' 
                                        lastMono = MonosacNamesSpecial[nMonoSpecial[0]]
                                        currentLength = currentLength + 1
                            
                            if specialRand >= 0.15:
                            
                                if MonosacNames[nMono[j]] == '[Ac(1-5)]aXNeup' or MonosacNames[nMono[j]] == '[Ac(1-5)]bXNeup':
                                    if lastMono == '[Ac(1-5)]aXNeup' or lastMono == '[Ac(1-5)]bXNeup':
                                        if currentLength < (GlycanLength[0]-1):
                                            GlycanName = str(MonosacNames[nMono[j]]) + '(2-4)' + GlycanName
                                            lastLinkage = '(2-4)' 
                                            lastMono = MonosacNames[nMono[j]]
                                            currentLength = currentLength + 1
                                        
                                    if lastMono != '[Ac(1-5)]aXNeup' and lastMono != '[Ac(1-5)]bXNeup':
                                        if currentLength < (GlycanLength[0]-1):
                                            GlycanName = str(MonosacNames[nMono[j]]) + '(2-3)' + GlycanName    
                                            lastLinkage = '(2-3)' 
                                            lastMono = MonosacNames[nMono[j]]                                
                                            currentLength = currentLength + 1
                                
                                if MonosacNames[nMono[j]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j]] != '[Ac(1-5)]bXNeup':
                                    
                                   # else: # (MonosacNames[nMono[j-1]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j-1]] != '[Ac(1-5)]bXNeup'):
                                        #Randlink = random.uniform(0, 1)
                                        if (MonosacNames[nMono[j]] == '[Ac(1-2)]aDGlcpN' or MonosacNames[nMono[j]] == '[Ac(1-2)]bDGlcpN') and Linkages[nLink[j-1]] != '(1-2)':
                                            if currentLength < (GlycanLength[0]-1):
                                                GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]])  + GlycanName
                                                lastLinkage = Linkages[nLink[j-1]]
                                                lastMono = MonosacNames[nMono[j]]
                                                currentLength = currentLength + 1
                                            
                                        else:
                                            branchRand = random.uniform(0, 1)
                                            if branchRand < 0.5: 
                                                if GlycanName[0] != '[': 
                                                    #if Linkages[nLink[j-1]] != lastLinkage:
                                                        # Ac(1-5)bXNeup(2-3)[bDXylp(1-4)]bDXylp(1-3)bDManp(1-3)[bDFucp(1-2)]aLFucp(1-3)[aDManp(1-4)]aDGlcp(1-2)bDGlcp(1-2)[Ac(1-5)]aXNeup(2-3)aDFucp(1-4)[Ac(1-5)]bXNeup(2-3)bDGalpA
                                                        if lastMono != '[Ac(1-5)]aXNeup' and lastMono != '[Ac(1-5)]bXNeup' and lastMono != '[S-3)]aDGalp' and lastMono != '[S-3)]bDGalp' and lastMono != '[Ac(1-2)]aDGlcpN' and lastMono != '[Ac(1-2)]bDGlcpN' :
                                                            if currentLength < (GlycanLength[0]-2):
                                                                GlycanName = '[' + str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]]) + ']'  + GlycanName
                                                                lastLinkage = Linkages[nLink[j-1]]
                                                                lastMono = MonosacNames[nMono[j]]
                                                                currentLength = currentLength + 1
                                                            
                                                        if ( ( Linkages[nLink[j-1]] != '(1-2)' and (lastMono == '[Ac(1-5)]aXNeup' or lastMono == '[Ac(1-5)]bXNeup') ) or ( Linkages[nLink[j-1]] != '(1-3)' and (lastMono == '[S-3)]aDGalp' or lastMono == '[S-3)]bDGalp')) or ( Linkages[nLink[j-1]] != '(1-2)' and (lastMono == '[Ac(1-2)]aDGlcpN' or lastMono == '[Ac(1-2)]bDGlcpN') ) ):
                                                            if currentLength < (GlycanLength[0]-1):
                                                                GlycanName = '[' + str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]]) + ']'  + GlycanName
                                                                lastLinkage = Linkages[nLink[j-1]]
                                                                lastMono = MonosacNames[nMono[j]]
                                                                currentLength = currentLength + 1
                                                        
                                                #print(GlycanName[0])
    #bDGalpA(1-3)bDGlcp(1-2)aDGalpA(1-3)bDManpA(1-2)[Ac(1-5)]aXNeup(2-3)[aDGlcpA(1-4)]aDGalp(1-3)bDManp(1-4)bDGlcp
                                            else:
                                                if GlycanName[0] != '[': 
                                                    if currentLength < (GlycanLength[0]-1):
                                                        GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]])  + GlycanName
                                                        lastLinkage = Linkages[nLink[j-1]]
                                                        lastMono = MonosacNames[nMono[j]]
                                                        currentLength = currentLength + 1
                                                 
                                                if (GlycanName[0] == '[' and Linkages[nLink[j-1]] != lastLinkage ) and (lastMono != '[Ac(1-5)]aXNeup' and lastMono != '[Ac(1-5)]bXNeup') and ~((Linkages[nLink[j-1]] == '(1-3)') and (lastMono == '[S-3)]aDGalp' or lastMono == '[S-3)]bDGalp')): 
                                                    if currentLength < (GlycanLength[0]-1):
                                                        GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]])  + GlycanName
                                                        lastLinkage = Linkages[nLink[j-1]]
                                                        lastMono = MonosacNames[nMono[j]]
                                                        currentLength = currentLength + 1
                                                    
                                                if Linkages[nLink[j-1]] == '(1-3)' and (lastMono == '[Ac(1-5)]aXNeup' or lastMono == '[Ac(1-5)]bXNeup'): # and GlycanName[0] != '[':
                                                    if currentLength < (GlycanLength[0]-1):
                                                        GlycanName = str(MonosacNames[nMono[j]]) + '(1-4)' + GlycanName
                                                        lastLinkage = '(1-4)' 
                                                        lastMono = MonosacNames[nMono[j]]   
                                                        currentLength = currentLength + 1
                                                '''
                                                if GlycanName[0] == '[' and Linkages[nLink[j-1]] == Linkages[nLink[j-2]]:
                                                    if nLink[j-1] > 0:
                                                        GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]-1])  + GlycanName  
                                                    if nLink[j-1] == 0:
                                                        Rand2 = random.uniform(0, 1)
                                                        if Rand2 < 0.5:
                                                            GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]+1])  + GlycanName
                                                        if Rand2 >= 0.5:
                                                            GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]+2])  + GlycanName    
                                                else:    
                                                    GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]])  + GlycanName
                                                '''
                                
                                        '''
                                        #Add (1-5) and (1-6) linkages later
                                        if Randlink < 0.15 and MonosacNames[nMono[j-1]] != 'aDXylp' and MonosacNames[nMono[j-1]] != 'bDXylp':
                                            if MonosacNames[nMono[j-1]] != 'bDXylp' 
                                                GlycanName = str(MonosacNames[nMono[j]]) + '(1-6)'  + GlycanName    
                                        #if Randlink >= 0.15 and Randlink < 0.30: 
                                           # GlycanName = str(MonosacNames[nMono[j]]) + '(1-5)'  + GlycanName  
                                        if Randlink >= 0.15:
                                            GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]])  + GlycanName
                                        '''    
                            
                        if j == (GlycanLength[0]-1) and (GlycanName[0] != '[' or (GlycanName[0] == '[' and Linkages[nLink[j-1]] != lastLinkage ) ) and ~(Linkages[nLink[j-1]] == '(1-3)' and (lastMono == '[S-3)]aDGalp' or lastMono == '[S-3)]bDGalp')):
                            
                            if MonosacNames[nMono[j]] == '[Ac(1-2)]aDGlcpN':
                                GlycanName = 'Ac(1-2)aDGlcpN' + str(Linkages[nLink[j-1]]) + GlycanName
                                currentLength = currentLength + 1
                                
                            if MonosacNames[nMono[j]] == '[Ac(1-2)]bDGlcpN':
                                GlycanName = 'Ac(1-2)bDGlcpN' + str(Linkages[nLink[j-1]]) + GlycanName
                                currentLength = currentLength + 1
                                
                            if MonosacNames[nMono[j]] == '[Ac(1-5)]aXNeup':
                                if MonosacNames[nMono[j-1]] == '[Ac(1-5)]aXNeup' or MonosacNames[nMono[j-1]] == '[Ac(1-5)]bXNeup':
                                    GlycanName = 'Ac(1-5)aXNeup' + '(2-4)' + GlycanName
                                    currentLength = currentLength + 1
                                if MonosacNames[nMono[j-1]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j-1]] != '[Ac(1-5)]bXNeup':
                                    GlycanName = 'Ac(1-5)aXNeup' + '(2-3)' + GlycanName
                                    currentLength = currentLength + 1
                            if MonosacNames[nMono[j]] == '[Ac(1-5)]bXNeup':
                                if MonosacNames[nMono[j-1]] == '[Ac(1-5)]aXNeup' or MonosacNames[nMono[j-1]] == '[Ac(1-5)]bXNeup':
                                    GlycanName = 'Ac(1-5)bXNeup' + '(2-4)' + GlycanName
                                    currentLength = currentLength + 1
                                if MonosacNames[nMono[j-1]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j-1]] != '[Ac(1-5)]bXNeup':
                                    GlycanName = 'Ac(1-5)bXNeup' + '(2-3)' + GlycanName
                                    currentLength = currentLength + 1
                                
                            if MonosacNames[nMono[j]] != '[Ac(1-2)]aDGlcpN' and MonosacNames[nMono[j]] != '[Ac(1-2)]bDGlcpN' and MonosacNames[nMono[j]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j]] != '[Ac(1-5)]bXNeup':    
                                GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]]) + GlycanName
                                currentLength = currentLength + 1
                    
                    if j == (GlycanLength[0]-1):
                        modificationRand = random.uniform(0, 1)
                        
                        # if  > 5, then leave the default -OH, automatically added, right now just 50/50 -OME vs -OH
                        if modificationRand < 0.5 : 
                            GlycanName = GlycanName + '(1-1)Me' # -OME
                            
                        if GlycanName not in GlycanList:
                            GlycanList.append(GlycanName)                        
                        #print(GlycanName)

        if OnlyLinear == True:
            if AllowXyl == True:
                
                nLink = np.random.randint(0,len(Linkages)-4,(GlycanLength[0]-1)) # to do just 1-2, 1-3, 1-4
                nMono = np.random.randint(0,len(MonosacNames),(GlycanLength[0]))
                
                GlycanName = ''
                
                for j in range(GlycanLength[0]):
                    #print(j)
                    
                    if j == 0:
                        GlycanName = str(MonosacNames[nMono[j]]) + GlycanName
                    if j > 0: # and j < (GlycanLength - 1): 
                        if j < (GlycanLength[0]-1):      
                            
                            specialRand = random.uniform(0, 1)
                            
                            if specialRand < 0.15:
                            
                                nMonoSpecial = np.random.randint(0,len(MonosacNamesSpecial),1)
                                specialRandlink = random.uniform(0, 1)
                                
                                if specialRandlink > 0.5:
                                    GlycanName = str(MonosacNamesSpecial[nMonoSpecial[0]]) + '(1-2)' + GlycanName
                                if specialRandlink <= 0.5:
                                    GlycanName = str(MonosacNamesSpecial[nMonoSpecial[0]]) + '(1-4)' + GlycanName    
                            
                            if specialRand >= 0.15:
                            
                                if MonosacNames[nMono[j]] == '[Ac(1-5)]aXNeup' or MonosacNames[nMono[j]] == '[Ac(1-5)]bXNeup':
                                    if MonosacNames[nMono[j-1]] == '[Ac(1-5)]aXNeup' or MonosacNames[nMono[j-1]] == '[Ac(1-5)]bXNeup':
                                        GlycanName = str(MonosacNames[nMono[j]]) + '(2-4)' + GlycanName
                                    if MonosacNames[nMono[j-1]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j-1]] != '[Ac(1-5)]bXNeup':
                                        GlycanName = str(MonosacNames[nMono[j]]) + '(2-3)' + GlycanName    
                                
                                if MonosacNames[nMono[j]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j]] != '[Ac(1-5)]bXNeup':
                                    if Linkages[nLink[j-1]] == '(1-3)' and (MonosacNames[nMono[j-1]] == '[Ac(1-5)]aXNeup' or MonosacNames[nMono[j-1]] == '[Ac(1-5)]bXNeup'):
                                        GlycanName = str(MonosacNames[nMono[j]]) + '(1-4)' + GlycanName
                                    else: # (MonosacNames[nMono[j-1]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j-1]] != '[Ac(1-5)]bXNeup'):
                                        #Randlink = random.uniform(0, 1)
                                        GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]])  + GlycanName
                                        
                                        '''
                                        #Add (1-5) and (1-6) linkages later
                                        if Randlink < 0.15 and MonosacNames[nMono[j-1]] != 'aDXylp' and MonosacNames[nMono[j-1]] != 'bDXylp':
                                            if MonosacNames[nMono[j-1]] != 'bDXylp' 
                                                GlycanName = str(MonosacNames[nMono[j]]) + '(1-6)'  + GlycanName    
                                        #if Randlink >= 0.15 and Randlink < 0.30: 
                                           # GlycanName = str(MonosacNames[nMono[j]]) + '(1-5)'  + GlycanName  
                                        if Randlink >= 0.15:
                                            GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]])  + GlycanName
                                        '''    
                            
                        if j == (GlycanLength[0]-1):
                            
                            if MonosacNames[nMono[j]] == '[Ac(1-2)]aDGlcpN':
                                GlycanName = 'Ac(1-2)aDGlcpN' + str(Linkages[nLink[j-1]]) + GlycanName
                                
                            if MonosacNames[nMono[j]] == '[Ac(1-2)]bDGlcpN':
                                GlycanName = 'Ac(1-2)bDGlcpN' + str(Linkages[nLink[j-1]]) + GlycanName
                                
                            if MonosacNames[nMono[j]] == '[Ac(1-5)]aXNeup':
                                if MonosacNames[nMono[j-1]] == '[Ac(1-5)]aXNeup' or MonosacNames[nMono[j-1]] == '[Ac(1-5)]bXNeup':
                                    GlycanName = 'Ac(1-5)aXNeup' + '(2-4)' + GlycanName
                                if MonosacNames[nMono[j-1]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j-1]] != '[Ac(1-5)]bXNeup':
                                    GlycanName = 'Ac(1-5)aXNeup' + '(2-3)' + GlycanName
                                
                            if MonosacNames[nMono[j]] == '[Ac(1-5)]bXNeup':
                                if MonosacNames[nMono[j-1]] == '[Ac(1-5)]aXNeup' or MonosacNames[nMono[j-1]] == '[Ac(1-5)]bXNeup':
                                    GlycanName = 'Ac(1-5)bXNeup' + '(2-4)' + GlycanName
                                if MonosacNames[nMono[j-1]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j-1]] != '[Ac(1-5)]bXNeup':
                                    GlycanName = 'Ac(1-5)bXNeup' + '(2-3)' + GlycanName
                                
                            if MonosacNames[nMono[j]] != '[Ac(1-2)]aDGlcpN' and MonosacNames[nMono[j]] != '[Ac(1-2)]bDGlcpN' and MonosacNames[nMono[j]] != '[Ac(1-5)]aXNeup' and MonosacNames[nMono[j]] != '[Ac(1-5)]bXNeup':    
                                GlycanName = str(MonosacNames[nMono[j]]) + str(Linkages[nLink[j-1]]) + GlycanName
                    
                    if j == (GlycanLength[0]-1):
                        modificationRand = random.uniform(0, 1)
                        
                        # if  > 5, then leave the default -OH, automatically added, right now just 50/50 -OME vs -OH
                        if modificationRand < 0.5 : 
                            GlycanName = GlycanName + '(1-1)Me' # -OME
                            
                        if GlycanName not in GlycanList:
                            GlycanList.append(GlycanName) 

    return GlycanList

############################    MAIN SCRIPT ############################################################

GlycanLibNames = [] #vector to add glycan names into from the preloaded library
NMR = 1 # whether to do NMR sim, 1 is yes
PDB = 1 # whether to get PDB files, 1 is yes
StartIteration = 23 #glycan list number to start from
MaxIteration = 900 # 100000 # how many glycans to do #PDB failed around 79 - 81, some in 90s, 169-174, around #207-211 had two possible structures but only did the first
anomer = '' #a, b or x right now, or blank
noCH2D = False
manualName =  False #"aLFucp(1-2)[Ac(1-2)aDGalpN(1-3)]bDGalp(1-3)[Ac(1-2)]bDGlcpN"
 # aDGalp(1-6)aDGlcpN(1-4)aDGlcpA 140
 # aDGalp(1-6)aDGlcpN(1-4)bDGlcpA 141
 # Ac(1-2)aDGalNA(1-4)aDGalp(1-6)aDGalp(1-3)aDGalp 100
 # bDGlcp(1-4)bDGlcpA(1-3)aDGalpA(1-4)aDGalp 143
Solvent = 'D2' #'DMSO'
UsePreloadedLibrary = False
DataDirect = "C:/Users/ryanbadman/Documents/GitHub/CASPERGlyoData/Nov2022/"
ReadFromFile = 1

if ReadFromFile == 0:
    NewGlycanList = GenerateNewGlycans(numGlycans=MaxIteration,MaxLength = 20)
    #random so save a copy of list
    with open(DataDirect+'NewGlycanList.txt', 'w') as f:
        for line in NewGlycanList:
            f.write(f"{line}\n")

if ReadFromFile == 1: 
    # Using readlines()
    #file1 = open(DataDirect+'NewGlycans_MaxLength20/NewGlycanList.txt', 'r')
    #file1 = open(DataDirect+'Conversion-GODESS.txt', 'r')
    #file1 = open(DataDirect+'sql_output_standard.txt', 'r')
    #file1 = open(DataDirect+'Glyco-nonlinear-v2.txt', 'r')
    file1 = open(DataDirect+'GlycoGODDESSconversion-linear-p2.txt', 'r')
    
    NewGlycanList = file1.readlines()
    count = 0
    # Strips the newline character
    for line in NewGlycanList:
        count += 1
        print("Line{}: {}".format(count, line.strip()))   
   
       
     

url = "http://csdb.glycoscience.ru/database/core/library.php#"
req = requests.get(url)
soup = BeautifulSoup(req.text, "html.parser")
print("The href links are :")
count = 0
for link in soup.find_all('a'):
   if link.get('href') is not None: 
       count = count + 1
       
       if count > 13 and count < 402:
           print(link.get('href'))
           split1 = link.attrs['onclick'].split("displayer.structure.value=",1)[1].split("displayer.submit()",1)[0]
           #split2 = split1.split("; displayer.submit()=",1)[0]
           #print(split1[1:(len(split1))])
           print(split1[1:(len(split1)-34)])
           GlycanLibNames.append(split1[1:(len(split1)-34)])


for k in range(len(GlycanLibNames)): 
   
    i = k + StartIteration
    if i < MaxIteration: # and i != 215:       
                   
        try: 
            if PDB == 1:
                #i=len(GlycanLibNames) - 1
                #glycanDir = DataDirect + str(GlycanLibNames[i]).replace("?","")  + '/'
                glycanDir = DataDirect + str(i)  + '/'               
                
                webpage = r"http://csdb.glycoscience.ru/database/core/search_struc.shtml"
                if UsePreloadedLibrary == True:
                    searchterm = GlycanLibNames[i]
                    print ('PDB count ', i,' glycan ', str(GlycanLibNames[i]))
                    if '?' in searchterm:
                        searchterm = searchterm.replace("?", anomer )
                        if searchterm[-1] == 'c' and (anomer == 'a' or anomer == 'b'):
                            searchterm = searchterm + 'p'
                        if searchterm[-1] == 'c' and (anomer == 'x'):
                            searchterm = searchterm + 'a'
                        glycanDir = DataDirect + str(i)  + anomer + '/' 
                        #searchterm = searchterm.replace("?", "b" )
                        
                    with open(DataDirect+'PreloadedLibraryGlycans.txt', 'w') as f:
                        for line in GlycanLibNames:
                            f.write(f"{line}\n")
                            
                if UsePreloadedLibrary == False:
                    searchterm = NewGlycanList[i]   
                    print ('PDB count ', i,' glycan ', str(NewGlycanList[i])) 
                    if ReadFromFile == 1:
                        searchterm = searchterm[0:(len(searchterm)-1)]
                    
                driver = webdriver.Chrome()
                driver.get(webpage)
                
                
                
                if manualName != False:
                    searchterm = manualName
                
                print()
                
                search_box = driver.find_element(By.ID, "structure")
                search_box.send_keys(searchterm)
                
                time.sleep(5)
               
                submit = driver.find_element(By.LINK_TEXT, "CSDB")
                submit.click()
             
                #http://csdb.glycoscience.ru/database/core/show_3d.php
                submit.click()
                #driver.find_element(By.XPATH,'//a[contains(@href,"show_3d")]').click()
                
                time.sleep(8)
                
                
                
                window_before = driver.window_handles[0]
                window_after = driver.window_handles[1]
                driver.switch_to.window(window_after)
                
                element_present = EC.presence_of_element_located((By.LINK_TEXT, 'SVG file'))                    
                WebDriverWait(driver, 60).until(element_present)
                
                if 'Parsing error:' in driver.page_source or 'Integrity error:' in driver.page_source or 'Fatal:' in driver.page_source:
                    print('ILLEGAL NAME ERROR')
                    element_present = EC.presence_of_element_located((By.ID, 'DOESNOTEXIST'))                    
                    WebDriverWait(driver, 1).until(element_present)
                
                driver.switch_to.window(window_before)
                
                if not os.path.exists(glycanDir):                
                    os.makedirs(glycanDir)
                
                html_from_page = driver.page_source
                soup = BeautifulSoup(html_from_page, 'html.parser')
                # print("The href links are :")
                count = 0
                for link in soup.find_all('a'):
                   if link.get('href') is not None: 
                       if link.get('href').startswith('show_3d'):
                           newHTML = link.get('href')
                           print(newHTML)                           
                                           
                new_webpage = r"http://csdb.glycoscience.ru/database/core/" + newHTML 
                driver2 = webdriver.Chrome()
                driver2.get(new_webpage) 
                http = urllib3.PoolManager()
                
                time.sleep(8)
                
                ids = driver2.find_elements(By.XPATH,'//*[@id]')
                for ii in ids:
                    #print ii.tag_name
                    #print('ii ', ii)
                    #print( ii.get_attribute('id') )   # id name as string
                    if re.search('smiles_selector', ii.get_attribute('id')):
                    #if re.search('smiles_container', ii.get_attribute('id')):   
                        dropdown_id = ii.get_attribute('id')
                        #print(dropdown_id)
                    
                
                #dropdown = Select(driver2.find_elements(By.CLASS_NAME,''))
                #print(dropdown)
                
                # find the frame using id, title etc.
                frame = driver2.find_elements(By.TAG_NAME,'iframe')
               # print(frame)
                
                #Get iframe 1 - this updates DRIVER to be within that iframe
                #WebDriverWait(driver, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, ".permission-core-iframe")))
                WebDriverWait(driver2, 300).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,'iframe')))
        
                #get iframe 2 - this can only be found when driver is inside the first iframe
                WebDriverWait(driver2, 300).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,'iframe')))
                
                #get iframe 2 - this can only be found when driver is inside the first iframe
                WebDriverWait(driver2, 300).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frame_3D")))
        
                #Wait for the button to fully load 
                button = WebDriverWait(driver2, 600).until(EC.element_to_be_clickable((By.LINK_TEXT, "PDB")))
        
                #click it
                button.click()
                
                time.sleep(3)
                window_before = driver2.window_handles[0]
                window_after = driver2.window_handles[1]
                driver2.switch_to.window(window_after)
                #print(html_from_page)
                
              #  print(driver2.find_element(By.XPATH, "/html/body").text)
                
                PDBcontent = driver2.find_element(By.XPATH, "/html/body").text
                
                with open(glycanDir+'PDB.pdb', 'w') as f:
                    f.write(PDBcontent)                
                 
                time.sleep(1)
                
                #driver2.quit()
                
                driver2.switch_to.window(window_before)
                
                if "chemically distinct structures. Please, select:" in driver2.page_source:
                    
                    print('two structures')
                    
                    
                    time.sleep(2)
                    #ids = driver2.find_elements(By.XPATH,'//*[@id]')
                    #elements = driver.find_elements(By.XPATH,"//table[@id = 'block_cosy']//td/a") 
                    dropdown = Select(driver2.find_element(By.ID,dropdown_id))
                    #print(dropdown)
                    dropdown.select_by_index(1) #.click()
                    driver2.find_element(By.ID,dropdown_id).click()
                    
                    element_present = EC.presence_of_element_located((By.LINK_TEXT, 'Show 3D'))                    
                    WebDriverWait(driver2, 60).until(element_present)
                    driver2.find_element(By.LINK_TEXT, 'Show 3D').click()
                    
                    '''
                    
                    new_webpage = r"http://csdb.glycoscience.ru/database/core/" + newHTML 
                    driver = webdriver.Chrome()
                    driver.get(new_webpage) 
                    http = urllib3.PoolManager()
                    
                    '''
                    
                    time.sleep(6)
                    
                    # find the frame using id, title etc.
                    frame = driver2.find_elements(By.TAG_NAME,'iframe')
                   # print(frame)
                    
                    #Get iframe 1 - this updates DRIVER to be within that iframe
                    #WebDriverWait(driver, 30).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, ".permission-core-iframe")))
                    WebDriverWait(driver2, 300).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,'iframe')))
            
                    #get iframe 2 - this can only be found when driver is inside the first iframe
                    WebDriverWait(driver2, 300).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,'iframe')))
                    
                    #get iframe 2 - this can only be found when driver is inside the first iframe
                    WebDriverWait(driver2, 300).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frame_3D")))
            
                    #Wait for the button to fully load 
                    button = WebDriverWait(driver2, 600).until(EC.element_to_be_clickable((By.LINK_TEXT, "PDB")))
            
                    #click it
                    button.click()
                    
                    time.sleep(3)
                    
                    window_after = driver2.window_handles[2]
                    driver2.switch_to.window(window_after)
                    #print(html_from_page)
                    
                  #  print(driver2.find_element(By.XPATH, "/html/body").text)
                    
                    PDBcontent2 = driver2.find_element(By.XPATH, "/html/body").text
                    
                    with open(glycanDir+'PDB2.pdb', 'w') as f:
                        f.write(PDBcontent2)                
                     
                    time.sleep(1)
                    
                    
                driver2.quit()
                driver.quit()
                
            if NMR == 1: # and i != 215:
                    #glycanDir = DataDirect + str(GlycanLibNames[i]).replace("?","")  + '/'
                    glycanDir = DataDirect + str(i)  + '/'
                    
                    ##################### SIMULATE ##################################
                    
                    webpage = r"http://csdb.glycoscience.ru/database/core/nmrsim.html" # edit me
                    #webpage = r"http://database/core/nmrsim.html" # edit me
                    
                    if UsePreloadedLibrary == True:
                        searchterm = GlycanLibNames[i]
                        print ('NMR count ', i,' glycan ', str(GlycanLibNames[i]))
                        if '?' in searchterm:
                            glycanDir = DataDirect + str(i)  + anomer + '/'
                            searchterm = searchterm.replace("?", anomer)
                            if searchterm[-1] == 'c' and (anomer == 'a' or anomer == 'b'):
                                searchterm = searchterm + 'p'
                            if searchterm[-1] == 'c' and (anomer == 'x'):
                                searchterm = searchterm + 'a'
                            #searchterm = searchterm.replace("?", "a" )
                    if UsePreloadedLibrary == False:
                        searchterm = NewGlycanList[i] 
                        print ('NMR count ', i,' glycan ', str(NewGlycanList[i]))
                        
                    
                    driver = webdriver.Chrome()
                    driver.get(webpage)
                    
                    if manualName != False:
                        searchterm = manualName
                    
                    search_box = driver.find_element(By.ID, "structure")
                    search_box.send_keys(searchterm)
                    search_box.submit()
                    
                    #time.sleep(2)
                    
                    #only do D2, otherwise default is Water or D2
                    if Solvent == 'D2':
                        select = Select(driver.find_element(By.ID,'solvent'))
                        # select by visible text
                        select.select_by_visible_text('Water-d2')                
                    
                    if Solvent == 'DMSO':
                        select = Select(driver.find_element(By.ID,'solvent'))
                        # select by visible text
                        select.select_by_visible_text('DMSO-d6')
                    
                    submit2 = driver.find_element(By.CLASS_NAME, "button_enh")
                    submit2.click()                
                    
                    time.sleep(5)
                    
                    #if 'Fatal' or 'Parsing error: missing main chain'  in driver.page_source:
                    if 'Parsing error:' in driver.page_source or 'Integrity error:' in driver.page_source or 'Fatal:' in driver.page_source:    
                        print('ILLEGAL NAME ERROR')
                        element_present = EC.presence_of_element_located((By.ID, 'DOESNOTEXIST'))                    
                        WebDriverWait(driver, 1).until(element_present)
                    
                    #time.sleep(20) # how long to allow the simulation to go for a given glycan
                    timeout = 600
                    element_present = EC.presence_of_element_located((By.ID, 'cosy_popmenu'))
                    WebDriverWait(driver, timeout).until(element_present)
                    
                    time.sleep(3) 
                    
                    if not os.path.exists(glycanDir):                
                        os.makedirs(glycanDir)
                    
                    ###########  TSV for hybrid empiricial/stats 1D carbon #####
                    
                    element_present = EC.presence_of_element_located((By.ID, 'tsv_hyb'))
                    WebDriverWait(driver, 120).until(element_present)
                    
                    c_tsv_hyb = driver.find_element(By.ID, "tsv_hyb")                              
                    #C_TSV.click()                
                    c_tsv_hyb_text = c_tsv_hyb.get_attribute('innerHTML')
                    #print( c_tsv_hyb_text.strip())
                    
                    with open(glycanDir+'c_tsv_hyb.txt', 'w') as f:
                        f.write(c_tsv_hyb_text)    
                        
                    #isPresent = driver.findElements(By.ID,'tsv_hyb').size() > 0
                    #if isPresent == False:
                        #pass
                        
                    
                    time.sleep(1) 
                    
                    ###########  TSV for empiricial 1D carbon #####
                    element_present = EC.presence_of_element_located((By.ID, 'tsv_emp'))
                    WebDriverWait(driver, 120).until(element_present)
                    c_tsv_emp = driver.find_element(By.ID, "tsv_emp")                              
                    #C_TSV.click()                
                    c_tsv_emp_text = c_tsv_emp.get_attribute('innerHTML')
                    #print( c_tsv_emp_text.strip())
                    
                    with open(glycanDir+'tsv_emp.txt', 'w') as f:
                        f.write(c_tsv_emp_text)                   
                        
                    
                    time.sleep(1) 
                    
                    ###########  TSV for stats 1D carbon #####
                    element_present = EC.presence_of_element_located((By.ID, 'tsv_statC'))
                    WebDriverWait(driver, 120).until(element_present)
                    c_tsv_stat = driver.find_element(By.ID, "tsv_statC")                              
                    #C_TSV.click()                
                    c_tsv_stat_text = c_tsv_stat.get_attribute('innerHTML')
                    #print( c_tsv_hyb_text.strip())
                    
                    with open(glycanDir+'c_tsv_stat.txt', 'w') as f:
                        f.write(c_tsv_stat_text)                   
                        
                    
                    time.sleep(1) 
                    
                    ###########  TSV for hybrid empiricial/stats 1D carbon #####
                    element_present = EC.presence_of_element_located((By.ID, 'tsv_statH'))
                    WebDriverWait(driver, 120).until(element_present)
                    h_tsv_stat = driver.find_element(By.ID, "tsv_statH")                              
                    #C_TSV.click()                
                    h_tsv_stat_text = h_tsv_stat.get_attribute('innerHTML')
                    #print( c_tsv_hyb_text.strip())
                    
                    with open(glycanDir+'h_tsv_stat.txt', 'w') as f:
                        f.write(h_tsv_stat_text)                   
                        
                    
                    time.sleep(1) 
                    
                    ##################### COSY ##################################
                    
                    elements = driver.find_elements(By.XPATH,"//table[@id = 'block_cosy']//td/a") 
                   # print(elements)
                    
                    #for element in elements:
                     #   print("COSY ", element.get_attribute("href"))
                    
                   # cosyJDX = driver.find_elements(By.ID, "cosy_popmenu")
                   # print(cosyJDX)
                    
                    #for element in cosyJDX:
                    #    print("COSY pop ", element.get_attribute("href"))        
                    
                    #print('1a ', cosyJDX)
                    
                    cosyJDX2 = driver.find_elements(By.LINK_TEXT, "JDX")
                    cosyJDX2help = driver.find_element(By.ID, "h72")
                    #cosyJDX3 = driver.find_element(By.LINK_TEXT,"Download file")
                    
                    #print('2a ',cosyJDX2)
                    
                    success = 0
                    j = -1
                    while success == 0:
                        j = j + 1
                        a = ActionChains(driver)
                        #identify element
                        #m = driver.find_element_by_link_text("Enabled")
                        #hover over element
                        element_present = EC.presence_of_element_located((By.LINK_TEXT, 'JDX'))                    
                        WebDriverWait(driver, 90).until(element_present)
                        a.move_to_element(cosyJDX2[j]).perform()
                        #identify sub menu element
                        element_present = EC.presence_of_element_located((By.LINK_TEXT, 'Download file'))                    
                        WebDriverWait(driver, 30).until(element_present)
                        n = driver.find_element(By.LINK_TEXT,"Download file")
                        # hover over element and click
                        a.move_to_element(n).click().perform()
                        a.move_to_element(cosyJDX2help).perform()
                        
                        
                        time.sleep(3) 
                        window_before = driver.window_handles[0]
                        window_after = driver.window_handles[1]
                        driver.switch_to.window(window_after)       
                                
                        elems = driver.find_elements(By.XPATH,"//a[@href]")
                        count = 0
                        for elem in elems:
                        #    print(count)
                            count = count + 1
                            #print(elem.get_attribute("href"))
                            if re.search('biopsel/jcamp/COSY',elem.get_attribute("href")):
                                jdxURL = elem.get_attribute("href")
                            #    print(jdxURL)
                                success = 1
                        if success != 1:
                            driver.close() 
                            
                    driver.get(jdxURL)        
                    #print(driver.find_element(By.XPATH, "/html/body").text)        
                    COSYcontent = driver.find_element(By.XPATH, "/html/body").text
                    
                    with open(glycanDir+'COSY.jdx', 'w') as f:
                        f.write(COSYcontent)
                    driver.close() 
                    time.sleep(3)
                    
                    ##################### TOCSY ##################################
                    
                    driver.switch_to.window(window_before) 
                    time.sleep(2)
                    
                    #tocsyJDX = driver.find_elements(By.ID, "tocsy_popmenu")
                    #print(tocsyJDX)
                    
                    #for element in tocsyJDX:
                    #    print("TOCSY pop ", element.get_attribute("href"))        
                    
                    #print('1a ', tocsyJDX)
                    
                    countXCheck = 0
                    lengthJDXButtons = 0
                    while lengthJDXButtons < 4 and countXCheck < 1200:
                        tocsyJDX2 = driver.find_elements(By.LINK_TEXT, "JDX")
                        tocsyJDX2help = driver.find_element(By.ID, "h72")
                        lengthJDXButtons = len(tocsyJDX2)
                        time.sleep(1)
                        countXCheck = countXCheck + 1
                    
                    success = 0
                    j = -1
                    while success == 0:
                        j = j + 1
                        driver.switch_to.window(window_before)
                        time.sleep(1)     
                        #tocsyJDX3 = driver.find_element(By.LINK_TEXT,"Download file")
                        
                        #print('2a ',tocsyJDX2, len(tocsyJDX2))
                        
                        a = ActionChains(driver)
                        #identify element
                        #m = driver.find_element_by_link_text("Enabled")
                        #hover over element
                        element_present = EC.presence_of_element_located((By.LINK_TEXT, 'JDX'))                    
                        WebDriverWait(driver, 90).until(element_present)
                        a.move_to_element(tocsyJDX2[j]).perform()
                        #identify sub menu element
                        element_present = EC.presence_of_element_located((By.LINK_TEXT, 'Download file'))                    
                        WebDriverWait(driver, 90).until(element_present)
                        n = driver.find_element(By.LINK_TEXT,"Download file")
                        # hover over element and click
                        a.move_to_element(n).click().perform()
                        a.move_to_element(tocsyJDX2help).perform()
                        
                        time.sleep(3) 
                        window_before = driver.window_handles[0]
                        window_after = driver.window_handles[1]
                        driver.switch_to.window(window_after)       
                                
                        elems = driver.find_elements(By.XPATH,"//a[@href]")
                        count = 0
                        for elem in elems:
                           # print('TOCSY test ', j)
                            count = count + 1
                           # print(elem.get_attribute("href"))
                            #print(jdxURL2)
                            if re.search('biopsel/jcamp/TOCSY',elem.get_attribute("href")):
                                jdxURL2 = elem.get_attribute("href")
                              #  print(jdxURL2)
                                success = 1
                        if success != 1:
                            driver.close()
                            
                    driver.get(jdxURL2)        
                    #print(driver.find_element(By.XPATH, "/html/body").text)        
                    TOCSYcontent = driver.find_element(By.XPATH, "/html/body").text
                    
                    with open(glycanDir+'TOCSY.jdx', 'w') as f:
                        f.write(TOCSYcontent)
                    
                    driver.close()     
                    time.sleep(3) 
                    
                    if noCH2D == False:
                    
                        ##################### edHSQC ##################################
                        
                        driver.switch_to.window(window_before) 
                        time.sleep(2)
                        
                        #hsqcJDX = driver.find_elements(By.ID, "hsqc_popmenu")
                        #print(hsqcJDX)
                        
                        #for element in hsqcJDX:
                        #    print("hsqc pop ", element.get_attribute("href"))        
                        
                        #print('1a ', hsqcJDX)
                        
                        lengthJDXButtons = 0
                        while lengthJDXButtons < 4:
                            hsqcJDX2 = driver.find_elements(By.LINK_TEXT, "JDX")
                            hsqcJDX2help = driver.find_element(By.ID, "h72")
                            lengthJDXButtons = len(hsqcJDX2)
                            time.sleep(1)
                        
                        
                        #hsqcJDX3 = driver.find_element(By.LINK_TEXT,"Download file")
                        
                      #  print('2a ',hsqcJDX2, len(hsqcJDX2))
                        
                        success = 0
                        j = -1
                        while success == 0:
                            
                            j = j + 1
                            driver.switch_to.window(window_before)
                            time.sleep(1)
                            a = ActionChains(driver)
                            #identify element
                            #m = driver.find_element_by_link_text("Enabled")
                            #hover over element
                            element_present = EC.presence_of_element_located((By.LINK_TEXT, 'JDX'))                    
                            WebDriverWait(driver, 90).until(element_present)
                            a.move_to_element(hsqcJDX2[j]).perform()
                            #identify sub menu element
                            n = driver.find_element(By.LINK_TEXT,"Download file")
                            # hover over element and click
                            a.move_to_element(n).click().perform()
                            a.move_to_element(hsqcJDX2help).perform()
                            
                            time.sleep(3) 
                            window_before = driver.window_handles[0]
                            window_after = driver.window_handles[1]
                            driver.switch_to.window(window_after)       
                                    
                            elems = driver.find_elements(By.XPATH,"//a[@href]")
                            count = 0
                            for elem in elems:
                          #      print('edHSQC test ', j)
                           #     print(count)
                                count = count + 1
                            #    print(elem.get_attribute("href"))
                                #print(jdxURL2)
                                if re.search('biopsel/jcamp/edHSQC',elem.get_attribute("href")):
                                    jdxURL3 = elem.get_attribute("href")
                         #           print(jdxURL3)
                                    success = 1
                            if success != 1:
                                driver.close()
                                
                        driver.get(jdxURL3)        
                       # print(driver.find_element(By.XPATH, "/html/body").text)        
                        edHSQCcontent = driver.find_element(By.XPATH, "/html/body").text
                        
                        with open(glycanDir+'edHSQC.jdx', 'w') as f:
                            f.write(edHSQCcontent)
                        driver. close()     
                        time.sleep(3)
                        
                        ##################### HMBC ##################################
                        
                        driver.switch_to.window(window_before)    
                        time.sleep(2)
                        #hmbcJDX = driver.find_elements(By.ID, "hmbc_popmenu")
                        #print(hmbcJDX)
                        
                       # for element in hmbcJDX:
                           # print("hmbc pop ", element.get_attribute("href"))        
                        
                        #print('1a ', hmbcJDX)
                        
                        lengthJDXButtons = 0
                        while lengthJDXButtons < 4:
                            hmbcJDX2 = driver.find_elements(By.LINK_TEXT, "JDX")
                            hmbcJDX2help = driver.find_element(By.ID, "h72")
                            lengthJDXButtons = len(hmbcJDX2)
                            time.sleep(1)
                        
                        
                        #hmbcJDX3 = driver.find_element(By.LINK_TEXT,"Download file")
                        
                        #print('2a ',hmbcJDX2, len(hmbcJDX2))
                        
                        success = 0
                        j = 4
                        while success == 0:
                            j = j - 1
                            #print('j ',j)
                            driver.switch_to.window(window_before)
                            time.sleep(1)
                            a = ActionChains(driver)
                            #identify element
                            #m = driver.find_element_by_link_text("Enabled")
                            #hover over element
                            element_present = EC.presence_of_element_located((By.LINK_TEXT, 'JDX'))                    
                            WebDriverWait(driver, 90).until(element_present)
                            a.move_to_element(hmbcJDX2[j]).perform()
                            #identify sub menu element
                            n = driver.find_element(By.LINK_TEXT,"Download file")
                            # hover over element and click
                            a.move_to_element(n).click().perform()
                            a.move_to_element(hmbcJDX2help).perform()
                            
                            time.sleep(3) 
                            window_before = driver.window_handles[0]
                            window_after = driver.window_handles[1]
                            driver.switch_to.window(window_after)       
                                    
                            elems = driver.find_elements(By.XPATH,"//a[@href]")
                            count = 0
                            for elem in elems:
                             #   print(count)
                                count = count + 1
                            #    print(elem.get_attribute("href"))
                                #print(jdxURL2)
                                if re.search('biopsel/jcamp/HMBC',elem.get_attribute("href")):
                                    jdxURL4 = elem.get_attribute("href")
                            #        print(jdxURL4)
                                    success = 1
                            if success != 1:
                                driver.close() 
                                
                        driver.get(jdxURL4)        
                      #  print(driver.find_element(By.XPATH, "/html/body").text)        
                        edHSQCcontent = driver.find_element(By.XPATH, "/html/body").text
                        
                        with open(glycanDir+'HMBC.jdx', 'w') as f:
                            f.write(edHSQCcontent)
                        
                    time.sleep(1)
                    driver.quit()
                    #time.sleep(300) 
            
        except TimeoutException or NoSuchElementException or StaleElementReferenceException or UnexpectedAlertPresentException:
            pass  # do nothing, TODO: log?
        
        
        
        
           

