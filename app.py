import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
from dotenv import load_dotenv

from src.utils.data import get_validators, get_proposals, get_validator_votes
from src.utils.data import prepare_complete_votes_df, compile_voting_history, format_voting_history, create_similarity_matrix

load_dotenv('.env')


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


def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


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
                osmosis_logo_svg = """<svg width="330" height="82" viewBox="0 0 194 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><path d="M52 27.1796C52 20.7044 56.743 16.0439 63.2594 16.0439C69.7758 16.0439 74.5187 20.7044 74.5187 27.1796C74.5187 33.6547 69.7758 38.3152 63.2594 38.3152C56.7842 38.3152 52 33.6547 52 27.1796ZM69.817 27.1796C69.817 23.1378 67.2187 20.0858 63.2594 20.0858C59.3 20.0858 56.743 23.1378 56.743 27.1796C56.743 31.1802 59.3 34.2734 63.2594 34.2734C67.2187 34.2321 69.817 31.1802 69.817 27.1796Z" fill="white"></path><path d="M76.2921 34.8893L78.7666 31.3837C80.2926 32.9509 82.6435 34.2707 85.613 34.2707C88.1288 34.2707 89.3661 33.1159 89.3661 31.8786C89.3661 28.0842 76.9519 30.6825 76.9519 22.5576C76.9519 18.9695 80.0452 16 85.1181 16C88.5412 16 91.387 17.0311 93.5317 19.0107L90.9746 22.3514C89.2424 20.743 86.8915 20.0006 84.7056 20.0006C82.726 20.0006 81.6537 20.8667 81.6537 22.1452C81.6537 25.5684 94.0266 23.2588 94.0266 31.3012C94.0266 35.2605 91.2221 38.23 85.4068 38.23C81.2825 38.3125 78.313 36.9102 76.2921 34.8893Z" fill="white"></path><path d="M115.885 37.9407V22.8458L109.823 37.9407H107.802L101.739 22.8458V37.9407H97.161V16.3706H103.595L108.833 29.4034L114.071 16.3706H120.546V37.8995H115.885V37.9407Z" fill="white"></path><path d="M123.722 27.1771C123.722 20.702 128.465 16.0415 134.981 16.0415C141.498 16.0415 146.241 20.702 146.241 27.1771C146.241 33.6523 141.498 38.3128 134.981 38.3128C128.465 38.3128 123.722 33.6523 123.722 27.1771ZM141.539 27.1771C141.539 23.1353 138.941 20.0833 134.981 20.0833C131.022 20.0833 128.465 23.1353 128.465 27.1771C128.465 31.1777 131.022 34.2709 134.981 34.2709C138.941 34.2297 141.539 31.1777 141.539 27.1771Z" fill="white"></path><path d="M148.014 34.8893L150.489 31.3837C152.014 32.9509 154.365 34.2707 157.335 34.2707C159.851 34.2707 161.088 33.1159 161.088 31.8786C161.088 28.0842 148.674 30.6825 148.674 22.5576C148.674 18.9695 151.767 16 156.84 16C160.263 16 163.109 17.0311 165.254 19.0107L162.696 22.3514C160.964 20.743 158.613 20.0006 156.428 20.0006C154.448 20.0006 153.376 20.8667 153.376 22.1452C153.376 25.5684 165.748 23.2588 165.748 31.3012C165.748 35.2605 162.944 38.23 157.129 38.23C153.004 38.3125 150.035 36.9102 148.014 34.8893Z" fill="white"></path><path d="M168.842 37.9407V16.3706H173.461V37.8995H168.842V37.9407Z" fill="white"></path><path d="M176.266 34.8893L178.74 31.3837C180.266 32.9509 182.617 34.2707 185.586 34.2707C188.102 34.2707 189.34 33.1159 189.34 31.8786C189.34 28.0842 176.925 30.6825 176.925 22.5576C176.925 18.9695 180.019 16 185.092 16C188.515 16 191.36 17.0311 193.505 19.0107L190.948 22.3514C189.216 20.743 186.865 20.0006 184.679 20.0006C182.699 20.0006 181.627 20.8667 181.627 22.1452C181.627 25.5684 194 23.2588 194 31.3012C194 35.2605 191.196 38.23 185.38 38.23C181.215 38.3125 178.245 36.9102 176.266 34.8893Z" fill="white"></path><path d="M43.8718 8.48521C43.3832 6.60355 41.8126 4.72189 38.9855 2.62722C36.7169 0.95858 34.3087 0 32.3891 0C32.0051 0 31.6561 0.0355013 31.3071 0.106507C30.4345 0.284022 29.6667 0.923075 29.1781 1.88166C28.5847 3.01775 28.4451 4.54438 28.8291 5.46746C28.9687 5.75148 29.1432 6.10651 29.3526 6.42603C27.5028 7.56213 26.4557 7.88166 26.3161 7.91716C31.1326 9.55029 35.1463 12.9586 37.6593 17.3964L37.6942 16.9704C37.7989 15.7988 38.1479 14.4497 38.6365 13.0651C39.1251 13.2071 39.6138 13.2781 40.1024 13.2781C41.3938 13.2781 42.5106 12.7456 43.2087 11.787C43.9067 10.8284 44.1859 9.5503 43.8718 8.48521Z" fill="#5E12A0"></path><path d="M38.846 12.0354C42.0221 12.9229 43.3134 10.4377 42.8946 8.76908C42.4409 7.10044 40.975 5.3963 38.3923 3.47914C35.8095 1.56198 33.1919 0.780915 31.5166 1.13594C29.8413 1.49097 29.3526 4.08269 29.7715 5.07677C29.946 5.4673 30.3299 6.03535 30.8534 6.6744C30.1903 7.13594 29.562 7.49097 29.0385 7.8105C32.2495 9.26612 35.0417 11.5383 37.1358 14.3785C37.3801 13.42 37.7291 12.5679 38.0432 11.8223C38.2875 11.8578 38.5668 11.9288 38.846 12.0354Z" fill="url(#paint0_radial)"></path><path d="M20.662 46.828C31.4372 46.828 40.1722 37.9426 40.1722 26.9819C40.1722 16.0212 31.4372 7.13574 20.662 7.13574C9.88676 7.13574 1.15173 16.0212 1.15173 26.9819C1.15173 37.9426 9.88676 46.828 20.662 46.828Z" fill="url(#paint1_radial)"></path><path opacity="0.6" d="M41.2891 7.13587C38.6366 4.29563 36.4029 3.55007 33.7154 2.94652C31.6213 2.44948 32.1797 1.24238 34.7276 1.4909C33.506 1.06486 32.3542 0.958353 31.5166 1.13587C29.8413 1.4909 29.3526 4.08261 29.7715 5.0767C29.946 5.46723 30.3299 6.03528 30.8534 6.67433C29.9111 7.31338 29.1083 7.77492 28.4452 8.12995C28.7593 8.27196 29.1432 8.44948 29.597 8.698C30.7836 9.33705 32.075 10.4021 32.075 10.4021C30.1205 8.698 30.5393 7.91693 33.2268 5.99977C34.0644 5.39622 35.6001 5.46723 37.0311 6.21279C38.4621 6.95835 40.1374 8.84001 40.1374 8.84001L38.5319 11.9643C38.6366 11.9998 38.7413 12.0353 38.846 12.0708C39.8582 12.3548 40.6609 12.2838 41.2891 12.0353C42.0221 11.5737 43.9417 10.0116 41.2891 7.13587Z" fill="#A98698"></path><path d="M33.6805 4.65085C34.3786 4.93488 35.286 5.43192 36.4029 6.17748C37.7292 7.06506 38.8809 8.05914 39.6139 8.8402C38.3923 10.4733 37.5895 12.71 37.1009 14.2722C37.3452 14.6272 37.6244 14.9822 37.8688 15.3372C38.1131 14.4497 38.5319 13.1361 39.0903 11.8224C39.2299 11.858 39.4044 11.858 39.579 11.858C39.9978 11.858 40.4864 11.7869 40.8703 11.4674C41.1495 11.2544 41.4637 10.8639 41.4288 10.1538C41.4288 9.47926 40.9052 8.62719 39.8233 7.5976C39.0554 6.85204 38.0084 6.03547 36.9613 5.28991C33.9597 3.26624 31.8656 2.69819 30.9233 3.65677C30.295 4.29582 30.3648 5.07689 30.5742 5.64494C29.4574 6.3905 28.515 6.92304 27.8868 7.27807C28.3056 7.42008 28.6895 7.5976 29.1084 7.77512C30.2252 7.17157 31.8307 6.14198 33.6805 4.65085ZM40.277 9.72778C40.3817 9.90529 40.4166 10.0828 40.4166 10.1893C40.4166 10.5088 40.3119 10.6154 40.2421 10.6864C40.1025 10.7929 39.8233 10.8639 39.579 10.8639C39.7884 10.4378 40.0327 10.0828 40.277 9.72778ZM31.6562 4.43784C31.7609 4.33133 32.0401 4.26032 32.4939 4.33133C32.1448 4.61535 31.7958 4.86387 31.4468 5.11239C31.4119 4.86387 31.4468 4.61535 31.6562 4.43784Z" fill="#5E12A0"></path><path d="M20.662 5.96436C9.24903 5.96436 0 15.3726 0 26.9821C0 38.5916 9.24903 47.9999 20.662 47.9999C32.075 47.9999 41.324 38.5916 41.324 26.9821C41.324 15.3726 32.0401 5.96436 20.662 5.96436ZM20.662 46.8283C9.87727 46.8283 1.15177 37.9525 1.15177 26.9821C1.15177 16.0117 9.87727 7.13595 20.662 7.13595C31.4467 7.13595 40.1722 16.0117 40.1722 26.9821C40.1722 37.9525 31.4118 46.8283 20.662 46.8283Z" fill="#5E12A0"></path><path opacity="0.6" d="M20.662 46.8285C31.4372 46.8285 40.1722 37.9431 40.1722 26.9824C40.1722 16.0217 31.4372 7.13623 20.662 7.13623C9.88676 7.13623 1.15173 16.0217 1.15173 26.9824C1.15173 37.9431 9.88676 46.8285 20.662 46.8285Z" fill="url(#paint2_linear)"></path><path opacity="0.6" d="M20.5224 44.4143C9.87724 42.6747 2.65252 32.4854 4.39762 21.657C5.16547 16.8641 7.5388 12.7812 10.8894 9.83447C6.00311 12.7102 2.37331 17.7161 1.39605 23.8226C-0.31415 34.651 6.91057 44.8404 17.5208 46.58C23.4541 47.5741 29.1781 45.6925 33.4012 42.0001C29.6667 44.2013 25.1294 45.1599 20.5224 44.4143Z" fill="#A98698"></path><path opacity="0.6" d="M23.7683 7.42024C18.8471 6.60367 14.0656 7.73977 10.1565 10.2605C10.0867 10.3315 10.0169 10.4025 10.0169 10.4025C11.5177 9.47941 13.7165 8.66285 13.7165 8.66285C8.06242 12.0001 6.31732 15.7989 6.31732 15.7989C8.51615 11.4676 14.973 8.41432 20.0338 8.20131C25.0946 7.98829 28.4103 9.51492 32.4589 12.8167C36.5076 16.154 38.9507 22.9705 38.7064 28.367C38.497 33.7634 35.7048 38.1303 35.7048 38.1303C37.6244 35.6096 38.7762 33.7634 39.5091 31.8818C39.6487 31.3137 39.7884 30.7457 39.8582 30.1421C41.6033 19.3492 34.4134 9.15989 23.7683 7.42024Z" fill="url(#paint3_linear)"></path><path d="M39.195 26.8047C39.195 37.2071 30.8883 45.6568 20.662 45.6568C10.4357 45.6568 2.09412 37.2071 2.09412 26.8047H39.195Z" fill="url(#paint4_linear)"></path><g opacity="0.6"><path opacity="0.6" d="M37.7291 26.8047C37.7291 36.9585 29.8413 45.2662 19.9291 45.6568C20.1734 45.6568 20.4177 45.6568 20.662 45.6568C30.8883 45.6568 39.195 37.2071 39.195 26.8047H37.7291Z" fill="url(#paint5_linear)"></path></g><g opacity="0.7"><path opacity="0.7" d="M4.71177 26.8047H2.09412C2.09412 37.2071 10.4008 45.6568 20.6271 45.6568C21.0808 45.6568 21.4996 45.6568 21.9185 45.6213C12.3204 44.9112 4.71177 36.7455 4.71177 26.8047Z" fill="url(#paint6_linear)"></path></g><path d="M39.1601 26.9822C39.1601 24.8166 35.4604 23.574 30.5393 23.1479C26.9793 22.8639 23.3843 23.2189 19.2659 24.497C15.7059 25.5621 12.4949 25.3846 10.1565 25.1006C4.95608 24.497 2.09412 24.426 2.09412 26.9822C2.09412 30.6745 9.49334 35.2899 20.5922 33.6923C26.2114 32.8757 29.1083 31.2071 32.424 30.071C36.0189 28.8639 39.1601 28.8994 39.1601 26.9822Z" fill="url(#paint7_linear)"></path><path d="M26.735 18.0356C28.4698 18.0356 29.8762 16.605 29.8762 14.8403C29.8762 13.0756 28.4698 11.645 26.735 11.645C25.0002 11.645 23.5938 13.0756 23.5938 14.8403C23.5938 16.605 25.0002 18.0356 26.735 18.0356Z" fill="white"></path><path d="M31.8656 20.414C32.5981 20.414 33.1919 19.81 33.1919 19.0649C33.1919 18.3198 32.5981 17.7158 31.8656 17.7158C31.1331 17.7158 30.5393 18.3198 30.5393 19.0649C30.5393 19.81 31.1331 20.414 31.8656 20.414Z" fill="white"></path><g opacity="0.6"><path opacity="0.6" d="M36.6122 12.2841C36.5773 12.2841 36.5424 12.2841 36.5424 12.2841C36.3329 12.2486 36.1933 12.0356 36.2282 11.787C36.5424 10.1539 37.8686 8.59176 37.9384 8.52076C38.0781 8.34324 38.3573 8.34324 38.4969 8.48526C38.6714 8.62727 38.6714 8.91129 38.5318 9.0533C38.4969 9.0888 37.2753 10.5444 36.9961 11.9645C36.9612 12.1776 36.7867 12.2841 36.6122 12.2841Z" fill="url(#paint8_linear)"></path></g><path opacity="0.2" d="M19.3729 41.787C19.9126 41.787 20.3501 41.3419 20.3501 40.7929C20.3501 40.2439 19.9126 39.7988 19.3729 39.7988C18.8332 39.7988 18.3956 40.2439 18.3956 40.7929C18.3956 41.3419 18.8332 41.787 19.3729 41.787Z" fill="white"></path><g opacity="0.4"><path opacity="0.6" d="M18.8122 41.4331C18.4283 41.0425 18.4283 40.4035 18.8122 40.013C18.882 39.942 18.9518 39.9065 19.0216 39.8354C18.882 39.871 18.7773 39.942 18.6726 40.0485C18.2887 40.439 18.2887 41.078 18.6726 41.4686C18.9867 41.7881 19.4753 41.8591 19.8593 41.6461C19.5102 41.7881 19.0914 41.7171 18.8122 41.4331Z" fill="url(#paint9_linear)"></path></g><path opacity="0.3" d="M19.7197 40.509C19.8353 40.509 19.9291 40.4137 19.9291 40.296C19.9291 40.1784 19.8353 40.083 19.7197 40.083C19.604 40.083 19.5103 40.1784 19.5103 40.296C19.5103 40.4137 19.604 40.509 19.7197 40.509Z" fill="white"></path><path opacity="0.2" d="M24.4686 41.2899C25.0083 41.2899 25.4458 40.8449 25.4458 40.2958C25.4458 39.7468 25.0083 39.3018 24.4686 39.3018C23.9289 39.3018 23.4913 39.7468 23.4913 40.2958C23.4913 40.8449 23.9289 41.2899 24.4686 41.2899Z" fill="white"></path><g opacity="0.4"><path opacity="0.6" d="M23.9079 40.9355C23.524 40.545 23.524 39.9059 23.9079 39.5154C23.9777 39.4444 24.0475 39.4089 24.1173 39.3379C23.9777 39.3734 23.873 39.4444 23.7683 39.5509C23.3844 39.9414 23.3844 40.5805 23.7683 40.971C24.0824 41.2906 24.571 41.3616 24.955 41.1485C24.6059 41.2906 24.1871 41.2195 23.9079 40.9355Z" fill="url(#paint10_linear)"></path></g><path opacity="0.3" d="M24.8154 40.012C24.931 40.012 25.0248 39.9166 25.0248 39.799C25.0248 39.6813 24.931 39.5859 24.8154 39.5859C24.6997 39.5859 24.606 39.6813 24.606 39.799C24.606 39.9166 24.6997 40.012 24.8154 40.012Z" fill="white"></path><path opacity="0.2" d="M21.9534 43.5976C22.3582 43.5976 22.6863 43.2638 22.6863 42.852C22.6863 42.4402 22.3582 42.1064 21.9534 42.1064C21.5486 42.1064 21.2205 42.4402 21.2205 42.852C21.2205 43.2638 21.5486 43.5976 21.9534 43.5976Z" fill="white"></path><g opacity="0.4"><path opacity="0.6" d="M21.5346 43.3147C21.2554 43.0306 21.2554 42.5336 21.5346 42.2496C21.5695 42.2141 21.6393 42.1786 21.6742 42.1431C21.5695 42.1786 21.4997 42.2496 21.4299 42.3206C21.1507 42.6046 21.1507 43.1016 21.4299 43.3857C21.6742 43.6342 22.0232 43.6697 22.3373 43.4922C22.0581 43.5987 21.744 43.5277 21.5346 43.3147Z" fill="url(#paint11_linear)"></path></g><path opacity="0.3" d="M22.1977 42.6034C22.2748 42.6034 22.3373 42.5398 22.3373 42.4613C22.3373 42.3829 22.2748 42.3193 22.1977 42.3193C22.1206 42.3193 22.0581 42.3829 22.0581 42.4613C22.0581 42.5398 22.1206 42.6034 22.1977 42.6034Z" fill="white"></path><path opacity="0.2" d="M26.4557 43.0649C26.8605 43.0649 27.1887 42.7311 27.1887 42.3193C27.1887 41.9075 26.8605 41.5737 26.4557 41.5737C26.0509 41.5737 25.7228 41.9075 25.7228 42.3193C25.7228 42.7311 26.0509 43.0649 26.4557 43.0649Z" fill="white"></path><g opacity="0.4"><path opacity="0.6" d="M26.0369 42.7819C25.7577 42.4979 25.7577 42.0009 26.0369 41.7169C26.0718 41.6814 26.1416 41.6459 26.1765 41.6104C26.0718 41.6459 26.002 41.7169 25.9322 41.7879C25.653 42.0719 25.653 42.5689 25.9322 42.853C26.1765 43.1015 26.5255 43.137 26.8396 42.9595C26.5604 43.066 26.2463 42.995 26.0369 42.7819Z" fill="url(#paint12_linear)"></path></g><path opacity="0.3" d="M26.7 42.0706C26.7771 42.0706 26.8396 42.0071 26.8396 41.9286C26.8396 41.8502 26.7771 41.7866 26.7 41.7866C26.6229 41.7866 26.5604 41.8502 26.5604 41.9286C26.5604 42.0071 26.6229 42.0706 26.7 42.0706Z" fill="white"></path><path opacity="0.2" d="M15.2173 41.4318C16.1039 41.4318 16.8227 40.7006 16.8227 39.7987C16.8227 38.8967 16.1039 38.1655 15.2173 38.1655C14.3306 38.1655 13.6118 38.8967 13.6118 39.7987C13.6118 40.7006 14.3306 41.4318 15.2173 41.4318Z" fill="white"></path><g opacity="0.4"><path opacity="0.6" d="M14.3107 40.8282C13.6825 40.1891 13.6825 39.1595 14.3107 38.5205C14.4154 38.414 14.5201 38.343 14.6597 38.272C14.4503 38.343 14.2758 38.485 14.1013 38.627C13.4731 39.2661 13.4731 40.2956 14.1013 40.9347C14.6248 41.4672 15.4276 41.5737 16.0558 41.1832C15.4625 41.4317 14.7644 41.3252 14.3107 40.8282Z" fill="url(#paint13_linear)"></path></g><path opacity="0.3" d="M15.7758 39.3019C15.9685 39.3019 16.1248 39.1429 16.1248 38.9468C16.1248 38.7507 15.9685 38.5918 15.7758 38.5918C15.583 38.5918 15.4268 38.7507 15.4268 38.9468C15.4268 39.1429 15.583 39.3019 15.7758 39.3019Z" fill="white"></path><path opacity="0.2" d="M29.5629 37.4201C30.4496 37.4201 31.1684 36.6889 31.1684 35.7869C31.1684 34.885 30.4496 34.1538 29.5629 34.1538C28.6763 34.1538 27.9575 34.885 27.9575 35.7869C27.9575 36.6889 28.6763 37.4201 29.5629 37.4201Z" fill="white"></path><g opacity="0.4"><path opacity="0.6" d="M28.6197 36.8165C27.9914 36.1774 27.9914 35.1478 28.6197 34.5088C28.7244 34.4023 28.8291 34.3313 28.9687 34.2603C28.7593 34.3313 28.5848 34.4733 28.4103 34.6153C27.782 35.2543 27.782 36.2839 28.4103 36.923C28.9338 37.4555 29.7365 37.562 30.3648 37.1715C29.7714 37.42 29.1083 37.3135 28.6197 36.8165Z" fill="url(#paint14_linear)"></path></g><path opacity="0.3" d="M30.1204 35.2901C30.3132 35.2901 30.4695 35.1312 30.4695 34.9351C30.4695 34.739 30.3132 34.5801 30.1204 34.5801C29.9277 34.5801 29.7714 34.739 29.7714 34.9351C29.7714 35.1312 29.9277 35.2901 30.1204 35.2901Z" fill="white"></path><defs><radialGradient id="paint0_radial" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(42.258 6.53236) scale(15.5992 15.8678)"><stop stop-color="#FFEAFF" stop-opacity="0.6"></stop><stop offset="0.6807" stop-color="#A087C9"></stop><stop offset="1" stop-color="#10002F"></stop></radialGradient><radialGradient id="paint1_radial" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(33.5794 13.2996) scale(38.1657 38.8229)"><stop stop-color="#FFEAFF" stop-opacity="0.6"></stop><stop offset="0.6807" stop-color="#A087C9"></stop><stop offset="1" stop-color="#10002F"></stop></radialGradient><linearGradient id="paint2_linear" x1="17.5324" y1="46.547" x2="23.9838" y2="7.41965" gradientUnits="userSpaceOnUse"><stop stop-color="#81FFFF"></stop><stop offset="0.6202" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint3_linear" x1="34.4118" y1="13.5042" x2="18.0272" y2="28.283" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint4_linear" x1="2.10982" y1="36.2197" x2="39.186" y2="36.2197" gradientUnits="userSpaceOnUse"><stop stop-color="#0002E9"></stop><stop offset="0.9952" stop-color="#FF00C7"></stop></linearGradient><linearGradient id="paint5_linear" x1="40.9411" y1="28.4589" x2="20.436" y2="47.5094" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint6_linear" x1="2.10982" y1="36.2197" x2="21.9454" y2="36.2197" gradientUnits="userSpaceOnUse"><stop stop-color="#000292"></stop><stop offset="0.9952" stop-color="#7D00C7"></stop></linearGradient><linearGradient id="paint7_linear" x1="2.13471" y1="28.5484" x2="39.1611" y2="28.5484" gradientUnits="userSpaceOnUse"><stop stop-color="#000292"></stop><stop offset="0.9952" stop-color="#BE00C7"></stop></linearGradient><linearGradient id="paint8_linear" x1="38.5535" y1="8.34786" x2="35.826" y2="12.7051" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint9_linear" x1="18.3837" y1="40.8245" x2="19.8603" y2="40.8245" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint10_linear" x1="23.4758" y1="40.3202" x2="24.9525" y2="40.3202" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint11_linear" x1="21.2159" y1="42.8616" x2="22.3245" y2="42.8616" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint12_linear" x1="25.7031" y1="42.3275" x2="26.8117" y2="42.3275" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint13_linear" x1="13.6141" y1="39.8402" x2="16.0256" y2="39.8402" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient><linearGradient id="paint14_linear" x1="27.9364" y1="35.8273" x2="30.348" y2="35.8273" gradientUnits="userSpaceOnUse"><stop offset="0.2888" stop-color="white"></stop><stop offset="0.7796" stop-color="white" stop-opacity="0"></stop></linearGradient></defs></svg>"""
                render_svg(osmosis_logo_svg)

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
