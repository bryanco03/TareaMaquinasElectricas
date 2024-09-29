import numpy as np
from math import sqrt


def deformacion(de, sc):
    #calculo para porcentaje de deformacion (df)
    df=((de)**2+2*sqrt(sc)*de+sc)/sc
    return df

def obtenerHEcuacion(a,b,B):
    H = B/(a-b*B)
    return H

def obtenerBEcuacion(a,b,H):
    B = a*H/(1+b*H)
    return B

def interpolarB(HDado, H, B):
    return np.interp(HDado, H, B)


def calcReluctancia(l, ur, At):
    r = l/( 4*np.pi*10**(-7)*ur*At)
    return r

def interpolarH(BDado, B, H):
    return np.interp(BDado, B, H)

def calcularI2Tabla(B,H,phi3, Sl, Sc, fap, Lg, L1,N1, I1, L2, N2, A, v, coef):
    resultados = []

    B3 = phi3/(Sc*fap)
    Lfe3 = A - Lg
    Ba = phi3/Sc
    H3 = interpolarH(B3, B, H)
    rg = calcReluctancia(Lg, 1, Sc*coef)
    F3 = Lfe3 * H3 + phi3*rg

    #B3 = phi3/(Sc*fap)
    #Lfe3 = A - Lg
    #Ba = phi3/(Sc*coef)
    #Ha = interpolarH(Ba, B, H)
    #H3 = interpolarH(B3, B, H)
    #F3 = Lfe3 * H3 + Ha*Lg
    H1 = (N1 * I1 - F3)/L1
    B1 = interpolarB(H1,H,B)
    phi1 = (B1*Sl*fap)/v
    resultados.append(phi1)
    phi2 = (phi3 - phi1) / v
    resultados.append(phi2)
    B2 = phi2/(Sl*fap)
    H2 = interpolarH(B2, B, H)
    I2 = (H2*L2+F3)/N2
    resultados.append(I2)
    return resultados

def calcularI2Ecuacion(a,b,phi3, Sl, Sc, fap, Lg, L1,N1, I1, L2, N2, A,v, coef):
    resultados = []

    B3 = phi3/(Sc*fap)
    Lfe3 = A - Lg
    Ba = phi3/Sc
    H3 = obtenerHEcuacion(a, b, B3) 
    rg = calcReluctancia(Lg, 1, Sc*coef)
    F3 = Lfe3 * H3 + phi3*rg


    #B3 = phi3/(Sc*fap)
    #Lfe3 = A - Lg
    #Ba = phi3/(Sc*coef)
    #Ha = obtenerHEcuacion(a, b, Ba)
    #H3 = obtenerHEcuacion(a, b, B3) 
    #F3 = Lfe3 * H3 + Ha*Lg
    H1 = (N1 * I1 - F3)/(2*L1 + A)
    B1 = obtenerBEcuacion(a, b, H1)
    phi1 = B1*Sl*fap/v
    resultados.append(phi1)
    phi2 = (phi3 - phi1)/v
    resultados.append(phi2)
    B2 = phi2/(Sl*fap)
    H2 = obtenerHEcuacion(a, b, B2)
    I2 = (H2*L2+F3)/N2
    resultados.append(I2)
    return resultados

def calcularI1Ecuacion(a,b,i2,n2,n1,l2,l1,Sc,Sl,phi3,A,Lg,fap, v, coef):
    resultados = []

    B3 = phi3/(Sc*fap)
    Lfe3 = A - Lg
    Ba = phi3/Sc
    H3 = obtenerHEcuacion(a, b, B3) 
    rg = calcReluctancia(Lg, 1, Sc*coef)
    F3 = Lfe3 * H3 + phi3*rg

    #B3 = phi3/(Sc*fap)
    #Lfe3 = A - Lg
    #Ba = phi3/(Sc*coef)
    #Ha = obtenerHEcuacion(a, b, Ba)
    #H3 = obtenerHEcuacion(a, b, B3) 
    #F3 = Lfe3 * H3 + Ha*Lg

    #cálculo de campo magnético de la culumna 2 (H2)
    h2=(n2*i2-F3)/(2*l2+A)
    #ecuación verdadera h2=(n2*i2-fmmAB)/(2*l2+a)

    #con interpolación se consigue la densidad de flujo 2 (b2)
    b2= obtenerBEcuacion(a, b, h2)
    #cálculo de flujo 2 (phi2)
    phi2=b2*Sl*fap/v
    resultados.append(phi2)
    phi1=(phi3-phi2)/v
    resultados.append(phi1)
    #cálculo de densidad de flujo 1 (b1)
    b1=phi1/Sl*fap
    #con interpolación se consigue el campo magnético en lazo 1 (h1)
    h1= obtenerHEcuacion(a, b, b1)
    #Se calcula la corriente i1
    i1=(h1*(2*l1+ A)+F3)/n1
    resultados.append(i1)
    #ecuación verdadera i1=(h1*(2*l1+a)+fmmAB)/n1

    return resultados


def calcularI1Tabla(H,B,i2,n2,n1,l2,l1,Sc,Sl,phi3,A,Lg,fap,v, coef):
    
    resultados = []

    B3 = phi3/(Sc*fap)
    Lfe3 = A - Lg
    Ba = phi3/Sc
    H3 = interpolarH(B3, B, H)
    rg = calcReluctancia(Lg, 1, Sc*coef)
    F3 = Lfe3 * H3 + phi3*rg




    #B3 = phi3/(Sc*fap)
    #Lfe3 = A - Lg
    #Ba = phi3/(Sc*coef)
    #Ha = interpolarH(Ba, B, H)
    #H3 = interpolarH(B3, B, H)
    #F3 = Lfe3 * H3 + Ha*Lg

    #cálculo de campo magnético de la culumna 2 (H2)
    h2=(n2*i2-F3)/(2*l2+A)
    #ecuación verdadera h2=(n2*i2-fmmAB)/(2*l2+a)

    #con interpolación se consigue la densidad de flujo 2 (b2)
    b2= interpolarB(h2,H,B)
    #cálculo de flujo 2 (phi2)
    phi2=b2*Sl*fap/v
    resultados.append(phi2)
    phi1=(phi3-phi2)
    resultados.append(phi1)
    #cálculo de densidad de flujo 1 (b1)
    b1=phi1/Sl*fap
    #con interpolación se consigue el campo magnético en lazo 1 (h1)
    h1= interpolarH(b1,B,H)
    #Se calcula la corriente i1
    i1=(h1*(2*l1+ A)+F3)/n1
    resultados.append(i1)
    #ecuación verdadera i1=(h1*(2*l1+a)+fmmAB)/n1

    return resultados






#H = [20, 40, 80, 160, 300, 600, 1200, 2000, 3000, 6000]
#B = [0.02, 0.2, 0.6, 0.9, 1.1, 1.24, 1.36, 1.45, 1.51, 1.6]
#phi3 = 0.02
#sl = 0.01
#sc = 0.02
#fap = 0.97
#lg = 0.002
#l1 = 1.10
#l2 = 1.10
#N1 = 100
#I1 = 20
#N2 = 50
#
#a = 1.2
#b = 2.4
#
#print(calcularI2Tabla(B,H,phi3,sl,sc,fap,lg,l1,N1,I1,l2,N2,0.30,v,coef))
#print(calcularI2Ecuacion(a,b,phi3,sl,sc,fap,lg,l1,N1,I1,l2,N2,0.30))