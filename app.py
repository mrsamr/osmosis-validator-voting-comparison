import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data import fetch_datasets
from utils.data import compile_voting_history, format_voting_history, create_similarity_matrix


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


    # Define data caching function
    @st.cache_data
    def load_data():
        return fetch_datasets()


    # Fetch datasets
    datasets = load_data()
    validators = datasets.get('validators')
    proposals_df = datasets.get('proposals_df')
    votes_df = datasets.get('votes_df')


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
            options = st.multiselect(label='Select validators', options=validators, default=None, format_func=lambda x: x['name'])

            
        # Voting history table
        with st.container():
            with st.container():
                with st.container():
                    st.subheader('Voting History')

                    if len(options) >= 1:
                        
                        # Checkbox input
                        show_all_proposals = st.checkbox('Show all proposals', value=False, help='Shows all proposals regardless of participation from selected validators.')

                        # Table prep
                        voting_history_df = compile_voting_history(votes_df, options)
                        formatted_voting_history_df = format_voting_history(voting_history_df, proposals_df, options, show_all_proposals)
                        
                        # Table output
                        st.dataframe(data=formatted_voting_history_df.style.applymap(highlight_vote), height=600, use_container_width=True)
                    
                    else:
                        st.markdown('Please select validators first.')


        # Voting similarity matrix
        with st.container():
            with st.container():
                with st.container():
                    st.subheader('Voting Similarity')

                    if len(options) >= 2:
                        vscol1, vscol2 = st.columns([2,10])

                        with vscol1:

                            # Checkbox input
                            overlap_only = st.checkbox('Overlap only', value=False, help='Calculates similarity across just the proposals where all selected validators voted on.')
                            divider(1)

                            # Change help texts depending on selected settings
                            if overlap_only:
                                help_text__num_proposals = 'The total number of governance proposals where all selected validators have voted on.'
                                help_text__exact_same_votes = 'The percentage of proposals where all selected validators voted exactly the same out of all proposals where all have voted on.'
                            else:
                                help_text__num_proposals = 'The total number of governance proposals where at least 1 of the selected validators have voted on.'
                                help_text__exact_same_votes = 'The percentage of proposals where all selected validators voted exactly the same out of all proposals where at least 1 voted.'


                            # Scorecards
                            selected_names = [v['name'] for v in options]
                            if overlap_only:
                                # Retain only the proposals where all selected validators have voted
                                filtered_voting_history_df = voting_history_df.loc[(voting_history_df.loc[:,selected_names].isnull()).mean(axis=1) == 0]
                            else:
                                # Retain all proposals where at least 1 validator has voted
                                filtered_voting_history_df = voting_history_df.loc[(voting_history_df.loc[:,selected_names].isnull()).mean(axis=1) < 1]

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
                                
                            st.metric(label='Intersection', value='{:.1%}'.format(intersection), help=help_text__exact_same_votes)


                        with vscol2:
                            with st.container():
                                similarity_df = create_similarity_matrix(options, filtered_voting_history_df)
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