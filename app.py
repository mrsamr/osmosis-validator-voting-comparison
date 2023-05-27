import streamlit as st
import pandas as pd
import plotly.express as px

from src.utils.data import get_validators, get_proposals, get_validator_votes
from src.utils.data import prepare_complete_votes_df, compile_voting_history, format_voting_history, create_similarity_matrix


def divider(n=1):
    """Returns an html divider object"""
    return st.write('<br />'*n, unsafe_allow_html=True)


def highlight_vote(vote):
    """Color-codes dataframe cells by vote"""
    if vote == 'YES':
        color = '#38761d'
    elif vote == 'NO':
        color = '#a72859'
    elif vote == 'NO WITH VETO':
        color = '#af1414'
    elif vote == 'ABSTAIN':
        color = '#40408c'
    else:
        color = '#140f34'
    return f'background-color: {color}'



if __name__ == '__main__':

    # Set Streamlit default settings
    st.set_page_config(layout='wide')

    # Load static files
    with open('static/styles.css', 'r') as file:
        css = file.read()
        
    with open('static/about.md', 'r') as file:
        about_md = file.read()
        
    with open('static/guide.md', 'r') as file:
        guide_md = file.read()
        
    with open('static/methodology.md', 'r') as file:
        methodology_md = file.read()
        
    with open('static/footer.html', 'r') as file:
        footer_html = file.read()
    
    # Apply custom CSS
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


    # Define data caching functions
    @st.cache_data
    def load_validators():
        return get_validators()
    
    @st.cache_data
    def load_proposals():
        return pd.DataFrame(get_proposals())
    
    @st.cache_data
    def load_votes(validators, proposals):
        votes = get_validator_votes()
        complete_votes = prepare_complete_votes_df(validators, proposals, votes)
        return complete_votes
    

    # Fetch datasets
    validators = load_validators()
    proposals = load_proposals()
    votes_df = load_votes(validators, proposals)
    
    proposals_df = pd.DataFrame(proposals)


    # Add left and right margins
    _, col, _ = st.columns([1,10,1])

    with col:

        # App header
        with st.container():
            tcol1, tcol2 = st.columns([3,9])

            # Osmosis logo
            with tcol1:
                st.image('https://app.osmosis.zone/_next/image?url=%2Fosmosis-logo-main.svg&w=384&q=75', width=330)

            # App name
            with tcol2:
                st.title('Validator Voting Comparison')
                

        # Validator select box
        with st.container():
            divider(1)
            
            scol1, scol2 = st.columns([9,3])
            
            with scol1:
                validator_selection = st.multiselect(label='Select validators', options=validators, default=None, format_func=lambda x: x['name'])

            with scol2:
                proposals_filter_options = [
                    {'id':'AT_LEAST_1_VOTED', 'label':'At least 1 has voted (among selected)'}, 
                    {'id':'ALL_VOTED',        'label':'All selected validators have voted'},
                    {'id':'ALL_PROPOSALS',    'label':'All governance proposals'},
                ]
                proposals_filter_selection = st.selectbox(label='Filter proposals', options=proposals_filter_options, format_func=lambda x: x['label'])
            
            
        # Voting history table (nested st.container for CSS selection)
        with st.container():
            with st.container():
                with st.container():
                    with st.container():
                        with st.container():
                            with st.container():
                                with st.container():
                                    st.subheader('Voting History')

                                    if len(validator_selection) >= 1:

                                        # Table prep
                                        voting_history_df = compile_voting_history(votes_df, proposals_df, validator_selection)
                                        filtered_voting_history_df = voting_history_df.copy()

                                        # Filter proposals
                                        if proposals_filter_selection['id'] == 'ALL_PROPOSALS':
                                            pass

                                        elif proposals_filter_selection['id'] == 'AT_LEAST_1_VOTED':
                                            filtered_voting_history_df = filtered_voting_history_df.loc[filtered_voting_history_df.notnull().mean(axis=1) > 0]

                                        elif proposals_filter_selection['id'] == 'ALL_VOTED':
                                            filtered_voting_history_df = filtered_voting_history_df.loc[filtered_voting_history_df.notnull().mean(axis=1) == 1]


                                        formatted_voting_history_df = format_voting_history(filtered_voting_history_df, validator_selection)

                                        # Table output
                                        st.dataframe(data=formatted_voting_history_df.style.applymap(highlight_vote), height=600, use_container_width=True)

                                    else:
                                        st.markdown('Please select validators first.')


        # Voting similarity matrix (nested st.container for CSS selection)
        with st.container():
            with st.container():
                with st.container():
                    with st.container():
                        with st.container():
                            with st.container():
                                with st.container():
                                    st.subheader('Voting Similarity')

                                    if len(validator_selection) >= 2:
                                        vscol1, vscol2 = st.columns([2,10])

                                        with vscol1:

                                            divider(1)

                                            # Change help texts depending on selected settings
                                            if proposals_filter_selection['id']=='ALL_PROPOSALS':
                                                help_text__num_proposals = 'The total number of governance proposals created to date.'
                                                help_text__intersection = 'The percentage of proposals where all selected validators voted exactly the same out of all proposals created to date.'
                                            elif proposals_filter_selection['id']=='AT_LEAST_1_VOTED':
                                                help_text__num_proposals = 'The total number of governance proposals where at least one of the selected validators has voted on.'
                                                help_text__intersection = 'The percentage of proposals where all selected validators voted exactly the same out of all proposals where at least one of the selected validators has voted on.'
                                            elif proposals_filter_selection['id']=='ALL_VOTED':
                                                help_text__num_proposals = 'The total number of governance proposals where all selected validators have voted on.'
                                                help_text__intersection = 'The percentage of proposals where all selected validators voted exactly the same out of all proposals where all selected validators have voted on.'


                                            # Scorecards
                                            selected_names = [v['name'] for v in validator_selection]
                                            num_proposals = filtered_voting_history_df.shape[0]
                                            st.metric(label='Proposals', value=num_proposals, help=help_text__num_proposals)
                                            divider(1)

                                            exact_same_votes = (filtered_voting_history_df.loc[:,selected_names].eq(filtered_voting_history_df.loc[:,selected_names[0]], axis=0).mean(axis=1)==1).sum()
                                            st.metric(label='Exact Same Votes', value=exact_same_votes, help='The number of proposals where all selected validators voted exactly the same.')
                                            divider(1)

                                            if num_proposals == 0:
                                                intersection = 0
                                            else:
                                                intersection = exact_same_votes / num_proposals

                                            st.metric(label='Intersection', value='{:.1%}'.format(intersection), help=help_text__intersection)


                                        with vscol2:
                                            with st.container():
                                                similarity_df = create_similarity_matrix(validator_selection, filtered_voting_history_df)
                                                fig = px.imshow(similarity_df, text_auto=True,
                                                                color_continuous_scale=px.colors.sequential.Greens,
                                                                range_color=(0,100))
                                                fig.update_layout(xaxis=dict(side='bottom', title=None),
                                                                  yaxis=dict(side='left', title=None, showgrid=False),
                                                                  height=min(800, 300+80*len(validator_selection)),
                                                                  paper_bgcolor='rgba(0,0,0,0)',
                                                                  plot_bgcolor='rgba(0,0,0,0)',
                                                                  margin=dict(t=60,b=20,l=20,r=20)
                                                                 )
                                                st.plotly_chart(fig, use_container_width=True)

                                    else:
                                        st.markdown('Please select multiple validators.')


                        # App info and usage notes
                        with st.container():

                            divider(2)

                            fcol1, fcol2, fcol3 = st.columns(3)

                            with fcol1:
                                with st.expander('About the app'):
                                    st.markdown(about_md)

                            with fcol2:
                                with st.expander('Usage Guide'):
                                    st.markdown(guide_md)

                            with fcol3:
                                with st.expander('Methodology'):
                                    st.markdown(methodology_md)


                        # Footer: quick links
                        with st.container():
                            divider(1)
                            st.markdown(footer_html, unsafe_allow_html=True)
