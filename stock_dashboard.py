pip install streamlit
import streamlit as st
import yfinance as yf
import plotly.graph_objs as go # For the candlestick plot
import plotly.express as px # For the normal plot

@st.cache_data
def stock_data(tickers, start_date, end_date):
    """
    Downloads stock data from yahoo finance. One-liner to take advantage of streamlit's caching

    :param tickers: The stock symbols to download
    :param start: Start date (incl.) as a string in the format YYYY-MM-DD
    :param end: End date (incl.) as a string in the format YYYY-MM-DD
    """
    df = yf.download(tickers, start=start_date, end=end_date, progress=False) # TODO progress bar?

    # if multiple tickers are present, convert to relative format (TODO)

    return df

@st.cache_data
def market_holidays():
    """
    Days the market is closed. I have this in its own function as one could imagine downloading this
    data from some web service...
    """
    return ['2023-10-01',
            '2023-10-07',
            '2023-10-08',
            '2023-10-14',
            '2023-10-15',
            '2023-10-21',
            '2023-10-22',
            '2023-10-28',
            '2023-10-29',
            '2023-11-04',
            '2023-11-05',
            '2023-11-11',
            '2023-11-12',
            '2023-11-18',
            '2023-11-19',
            '2023-11-23',
            '2023-11-25',
            '2023-11-26']

def app():
    # Artificially limit the tickers to the Dow Jones Industrial Average
    allowed_tickers = ['AXP', 'AMGN', 'AAPL', 'BA', 'CAT', 'CSCO', 'CVX', 'DOW', 'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ', 'KO', 'JPM', 'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 'UNH', 'CRM', 'VZ', 'V', 'WBA', 'WMT', 'DIS']

    # Initialize tickers, start, & end date if this is the first render
    sstate = st.session_state
    if 'tickers' not in sstate:
        sstate['tickers'] = ['AAPL']
        sstate['start'] = '2023-10-01'
        sstate['end'] = '2023-12-01'

    options = st.multiselect(
            label='Choose stocks:',
            options=allowed_tickers,
            default=sstate['tickers'],
            on_change=update_chart,
            # disabled=st.session_state.disabled,
            key='sel_tickers')


    # Pull data for the current selection of tickers
    df = stock_data(sstate['tickers'], sstate['start'], sstate['end'])

    if len(sstate['tickers']) == 1:
        # Show a pretty candlestick chart for a single selection
        fig = go.Figure(
                data=[go.Candlestick(x=df.index,
                                     open=df['Open'],
                                     high=df['High'],
                                     low=df['Low'],
                                     close=df['Close'])])
        fig.update_layout(title=f"Daily {sstate['tickers'][0]} price",
                                        xaxis_rangeslider_visible=False)
        fig.update_xaxes(rangebreaks=[{'values': market_holidays()}])
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Compute a relative price plot; move date index into column
        rel_df = df['Close'] / df['Close'].iloc[0]
        rel_df = rel_df.reset_index()
        rel_df.rename(columns={'index': 'Date'})

        fmt_tickers = ','.join(sstate['tickers'])
        fig = px.line(rel_df, x='Date', y=sstate['tickers'], title="Tickers {fmt_tickers}")
        fig.update_xaxes(rangebreaks=[{'values': market_holidays()}])
        st.plotly_chart(fig, use_container_width=True)

def update_chart(**kwargs):
    st.session_state['tickers'] = st.session_state['sel_tickers']

if __name__ == '__main__':
    app()


