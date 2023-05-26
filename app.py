import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from itertools import permutations
from utils.data import fetch_datasets


st.set_page_config(layout='wide')

st.markdown(
    """
    <style>
        #validator-voting-comparison {
            text-align: end;
            font-size: 2em;
            font-weight: 600;
        }
        
        div.css-16nc0hx.e1tzin5v1 > div:nth-child(1) > div > div:nth-child(3) > div > div:nth-child(1) > div {
            border:10px;
            padding:30px;
            border-radius:10px;
            background:#28274F;
        } 
        
        div.css-16nc0hx.e1tzin5v1 > div:nth-child(1) > div > div:nth-child(4) > div > div:nth-child(1) > div {
            border:10px;
            padding:30px;
            border-radius:10px;
            background:#28274F;
        } 
        
        div.css-16nc0hx.e1tzin5v1 > div:nth-child(1) > div > div:nth-child(5) > div > div:nth-child(1) > div {
            border:10px;
            padding:30px;
            border-radius:10px;
            background:#28274F;
        } 
        
        div.css-16nc0hx.e1tzin5v1 > div:nth-child(1) > div {
            border:10px;
            border-radius:10px;
            background:#140f34;
        }
        
        footer {
            display: none;
        }
        
        .viewerBadge_container__1QSob {
            display: none;
        }
        
    </style>
    """,
    unsafe_allow_html=True
)



def divider(n=1):
    return st.write('<br />'*n, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return fetch_datasets()


def highlight_vote(val):
    if val == 'YES':
        color = '#38761d'
    elif val == 'NO':
        color = '#a72859'
    elif val == 'NO WITH VETO':
        color = '#af1414'
    elif val == 'ABSTAIN':
        color = '#40408c'
    else:
        color = '#140f34'
    return f'background-color: {color}'


def create_voting_matrix(options, proposals_df):
    options_df = pd.DataFrame(options)
    selected_names = [x['name'] for x in options]
    missing_names = [n for n in selected_names if n not in votes_df['validator_name'].drop_duplicates().tolist()]
    filtered_votes_df = votes_df.merge(options_df, how='inner', left_on='validator_address', right_on='address')
    comparison_df = filtered_votes_df.pivot(index='proposal_id', columns='validator_name', values='vote').fillna('-')
    for mn in missing_names: comparison_df[mn] = '-'
    comparison_df = comparison_df.reset_index().rename_axis(None, axis=1)    
    comparison_df = comparison_df.merge(proposals_df, how='right', left_on='proposal_id', right_on='id')
    comparison_df = comparison_df.drop('proposal_id', axis=1).rename(columns={'id':'proposal_id'})
    comparison_df = comparison_df.fillna('-')
    comparison_df['title'] = 'Prop #' + comparison_df['proposal_id'].astype('str') + ' - ' + comparison_df['title'].fillna('')  
    
    return comparison_df


def format_voting_matrix(options, comparison_df, show_all_proposals=False):
    selected_names = [x['name'] for x in options]
    display_comparison_df = comparison_df.copy()
    display_comparison_df['proposal_id'] = display_comparison_df['proposal_id'].astype('str').str.rjust(5)
    display_comparison_df = display_comparison_df.rename(columns={'proposal_id':'ID', 'title':'Proposal'})
    display_comparison_df = display_comparison_df.set_index(['ID','Proposal'])
    display_comparison_df = display_comparison_df.sort_index(ascending=False)
    display_comparison_df = display_comparison_df[[v for v in selected_names if v in display_comparison_df.columns.tolist()]]
    display_comparison_df.columns = [v.ljust(18) if len(v)<=18 else v[:15]+'...' for v in display_comparison_df.columns]
    
    if show_all_proposals == False:
        display_comparison_df = display_comparison_df.loc[(display_comparison_df == '-').mean(axis=1) < 1.0]

    return display_comparison_df


def create_similarity_matrix(options, comparison_df, overlap_only=False):
    selected_names = [x['name'] for x in options]
    pairs = list(permutations(selected_names, 2))
    similarity_scores = []

    for p in pairs:
        pair_votes = comparison_df[[p[0],p[1]]]
        if overlap_only:
            pair_votes = pair_votes.loc[np.logical_and(pair_votes.iloc[:,0] != '-', pair_votes.iloc[:,1] != '-')]
        else:
            pair_votes = pair_votes.loc[np.logical_or(pair_votes.iloc[:,0] != '-', pair_votes.iloc[:,1] != '-')]
            
        num_proposals = pair_votes.shape[0]
        similarity = (pair_votes.iloc[:,0] == pair_votes.iloc[:,1]).mean()

        similarity_scores.append({'validator_0':p[0],
                                  'validator_1':p[1],
                                  'num_proposals':num_proposals,
                                  'similarity':similarity})

    similarity_df = pd.DataFrame(similarity_scores)
    similarity_df = similarity_df.pivot(index='validator_0', columns='validator_1', values='similarity')
    similarity_df = similarity_df.loc[selected_names, selected_names]
    similarity_df = similarity_df.fillna(0)
    similarity_df.columns.name = 'Validator A'
    similarity_df.index.name = 'Validator B'

    n = similarity_df.shape[0]
    for idx in range(n):
        similarity_df.iloc[idx,idx] = 1
        similarity_df.iloc[:idx,idx] = None

    similarity_df = (similarity_df * 100).round(2)
    
    return similarity_df


# Fetch datasets
datasets = load_data()
validators = datasets.get('validators')
proposals_df = datasets.get('proposals_df')
votes_df = datasets.get('votes_df')


_, col, _ = st.columns([1,10,1])

with col:
    
    tcol1, tcol2 = st.columns([3,9])
    with tcol1:
        st.image('https://app.osmosis.zone/_next/image?url=%2Fosmosis-logo-main.svg&w=384&q=75', width=330)
    with tcol2:
        st.title('Validator Voting Comparison')

    with st.container():
        divider(1)
        options = st.multiselect(label='Select validators', options=validators,
                                 default=None, format_func=lambda x: x['name'])
        

    with st.container():
        with st.container():
            with st.container():
                st.subheader('Voting History')
                
                if len(options) >= 1:
                    show_all_proposals = st.checkbox('Show all proposals', value=False, help='Shows all proposals regardless of participation from selected validators.')
                    
                    comparison_df = create_voting_matrix(options, proposals_df)
                    display_comparison_df = format_voting_matrix(options, comparison_df, show_all_proposals)
                    st.dataframe(data=display_comparison_df.style.applymap(highlight_vote), height=600, use_container_width=True)
                else:
                    st.markdown('Please select validators first.')

            
    
    with st.container():
        with st.container():
            with st.container():
                st.subheader('Voting Similarity')
                
                if len(options) >= 2:
                    simcol1, simcol2 = st.columns([2,10])
                    
                    with simcol1:
                        
                        # Overlap only toggle switch
                        overlap_only = st.checkbox('Overlap only', value=False, help='Calculates similarity across just the proposals where all selected validators voted on.')
                        divider(1)
                        
                        if overlap_only:
                            help_text__num_proposals = 'The total number of governance proposals where all selected validators have voted on.'
                            help_text__exact_same_votes = 'The percentage of proposals where all selected validators voted exactly the same out of all proposals where all have voted on.'
                        else:
                            help_text__num_proposals = 'The total number of governance proposals where at least 1 of the selected validators have voted on.'
                            help_text__exact_same_votes = 'The percentage of proposals where all selected validators voted exactly the same out of all proposals where at least 1 voted.'
                        
                        
                        # Scorecards
                        selected_names = [v['name'] for v in options]
                        if overlap_only:
                            filtered_comparison_df = comparison_df.loc[(comparison_df.loc[:,selected_names] == '-').mean(axis=1) == 0]
                        else:
                            filtered_comparison_df = comparison_df.loc[(comparison_df.loc[:,selected_names] == '-').mean(axis=1) < 1]
                        
                        num_proposals = filtered_comparison_df.shape[0]
                        st.metric(label='Proposals', value=num_proposals, help=help_text__num_proposals)
                        divider(1)

                        exact_same_votes = (filtered_comparison_df.loc[:,selected_names].eq(filtered_comparison_df.loc[:,selected_names[0]], axis=0).mean(axis=1)==1).sum()
                        st.metric(label='Exact Same Votes', value=exact_same_votes, help='The number of proposals where all selected validators voted exactly the same.')
                        divider(1)

                        if num_proposals == 0:
                            intersection = 0
                        else:
                            intersection = exact_same_votes / num_proposals
                        st.metric(label='Intersection', value='{:.1%}'.format(intersection), help=help_text__exact_same_votes)


                    with simcol2:
                        with st.container():
                            similarity_df = create_similarity_matrix(options, comparison_df, overlap_only)
                            fig = px.imshow(similarity_df, text_auto=True,
                                            color_continuous_scale=px.colors.sequential.Greens,
                                            range_color=(0,100))
                            fig.update_layout(xaxis=dict(side='bottom', title=None),
                                              yaxis=dict(side='left', title=None, showgrid=False),
                                              height=min(800, 300+100*len(options)),
                                              paper_bgcolor='rgba(0,0,0,0)',
                                              plot_bgcolor='rgba(0,0,0,0)',
                                              margin=dict(t=60,b=20,l=20,r=20)
                                             )
                            st.plotly_chart(fig, use_container_width=True)

                else:
                    st.markdown('Please select multiple validators.')
                        
    
    divider(2)
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        with st.expander('About the app'):
            about_text = r'''
This app enables you to compare multiple validators based on their voting history.

This was built by [@rmas](https://twitter.com/rmas_11) as an open-source contribution to [MetricsDAO](https://metricsdao.xyz) and to the community in general. 
Please reach out on Twitter if you have any questions or if you would like to collaborate.

'''
            st.markdown(about_text)
            
    with fcol2:
        with st.expander('Usage Guide'):
            guide_text = r'''
1. Select the names of the validators you want to compare. You may select as many as your browser can handle.
1. `Voting History` displays the votes of your selected validators side-by-side across all proposals where at least 1 validator has voted in.
1. `Voting Similarity` displays similarity scores between all pairs of validators among the ones you selected.
1. Data is refreshed every 6 hours.
            '''
            st.markdown(guide_text)
           
    with fcol3:
        with st.expander('Methodology'):
            methodology_text = r'''
The app code and SQL statements are all open-source and available at this [Github repo](https://github.com/mrsamr/osmosis-validator-voting-comparison).

- Data provider: [Flipside Crypto](https://flipsidecrypto.xyz)
- Front-end app: [Streamlit](http://streamlit.io)

            '''
            st.markdown(methodology_text)
        
                        
    with st.container():
        divider(1)
        st.markdown('<center>Created by <strong>rmas</strong>  |  <a href="https://github.com/mrsamr/osmosis-validator-voting-comparison"> Github</a>  |  <a href="https://twitter.com/rmas_11">Twitter</a>  |  <a href="https://flipsidecrypto.xyz/rmas">Flipside</a></center>', unsafe_allow_html=True)