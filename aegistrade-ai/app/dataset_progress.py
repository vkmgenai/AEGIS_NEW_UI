"""Read-only progress for public-data preparation, separate from C2 inference."""
import streamlit as st


def render_preparation_progress(key,initial,fetch):
    polling=initial.get('status') in {'QUEUED','PREPARING'}
    @st.fragment(run_every=5 if polling else None)
    def panel():
        job=initial
        if polling:
            try:job=fetch('/market/dataset?universe_id='+key,timeout=10).get('preparation') or initial
            except Exception:st.warning('Could not refresh public-data preparation; manual refresh remains available.')
        st.write('Data preparation: '+job['status'])
        st.caption(job.get('message',''))
        if job.get('error'):st.warning(job['error']+': '+job.get('error_detail',''))
        if polling and job['status'] not in {'QUEUED','PREPARING'}:st.rerun()
    panel()
