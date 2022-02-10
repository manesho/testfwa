import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

p_prl_n = pd.read_pickle('p_prl_n.pkl')
p_prl_t = pd.read_pickle('p_prl_t.pkl')
p_prl_w = pd.read_pickle('p_prl_w.pkl')
p_srl = pd.read_pickle('p_srl.pkl')

T_W = 168
T_N = 88
T_T = 80




def evaluate_model(P_PRL_S = 2, P_PRL_K= 3, D_P_SRL_K = -1, f_WK=0.2 ):
    D_P_SRL_O = f_WK *D_P_SRL_K
    p_prl_n.index.rename(['Y','KW'], inplace=True)
    p_prl_t.index.rename(['Y','KW'], inplace=True)

    df_results= pd.DataFrame()
    df_results['Einnahmen_S']=T_W * P_PRL_S * p_prl_w.reset_index(drop=True).Preis
    df_results['Einnahmen_K']= T_W * P_PRL_K * p_prl_w.reset_index(drop=True).Preis + T_W* D_P_SRL_K *p_srl.Preis
    df_results['Einnahmen_opt1']=np.maximum( df_results['Einnahmen_K'], df_results['Einnahmen_S'] )
    df_results['Einnahmen_opt2_winter'] = P_PRL_S*p_prl_n.reset_index().Preis*T_N+P_PRL_K*p_prl_t.reset_index().Preis*T_T + D_P_SRL_O* p_srl.Preis*T_W

    df_results['KW']=p_prl_w.reset_index().week

    df_results['datum']= pd.Timestamp('2020-01-01')+7*df_results.index*pd.Timedelta('1d')

    df_results['istwinter']=(df_results.KW<18) | (df_results.KW>40)
    df_results['Einnahmen_opt2']=df_results['Einnahmen_opt1']
    df_results['Einnahmen_opt2'].loc[df_results.istwinter]=df_results.loc[df_results.istwinter].Einnahmen_opt2_winter.copy()
    
    fig=px.line(data_frame=df_results.drop(columns=['istwinter']).rename(columns={'Einnahmen_S':'Standalone', 'Einnahmen_K':'Kombi', 'Einnahmen_opt2':'Opt2'}),
        x='datum',
        y=['Opt2', 'Standalone', 'Kombi'],
        template='simple_white',
         width=800, height=400,
        labels={'value':'Wocheneinnahmen [SFr]' ,'variable':'Szenario', 'datum':''}
        )
    return {'Figure':fig,
        'Einnahmen_S_tot': df_results.Einnahmen_S.sum(),
        'Einnahmen_K_tot': df_results.Einnahmen_K.sum(),
        'Einnahmen_opt1_tot': df_results.Einnahmen_opt1.sum(),
        'Einnahmen_opt2_tot': df_results.Einnahmen_opt2.sum(),
    } 
 
 

P_PRL_S = st.sidebar.slider('P_PRL_S', 0.,5.,2., step = 0.1)
P_PRL_K = st.sidebar.slider('P_PRL_K', P_PRL_S,5.,3., step = 0.1 )
f_WK = st.sidebar.slider('Szenario Opt2 : f_WK',0.,1.,0.2, step =0.01 )

results = evaluate_model(P_PRL_S = P_PRL_S, P_PRL_K = P_PRL_K , D_P_SRL_K = - (P_PRL_K-P_PRL_S))
st.plotly_chart(results['Figure'])
 
for key,value in results.items():
    if not key == 'Figure':
        st.markdown(key+' : {:.0f}'.format(value))
