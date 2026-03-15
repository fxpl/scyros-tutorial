from pathlib import Path

import streamlit as st
import subprocess
import re
import os
import polars as pl



def run_command(command: str, id: int, output: bool = True) -> None:
    st.markdown(f"```bash\n{command}\n```")

    state_key = f"cmd_state_{id}"
    output_key = f"cmd_output_{id}"
    rc_key = f"cmd_rc_{id}"

    if state_key not in st.session_state:
        st.session_state[state_key] = "idle"
    if output_key not in st.session_state:
        st.session_state[output_key] = ""
    if rc_key not in st.session_state:
        st.session_state[rc_key] = None

    slot = st.empty()

    # Always render persisted output if requested and available
    if output and st.session_state[output_key]:
        with st.expander("Command Output", expanded=True):
            st.code(st.session_state[output_key], language=None)

    # Always render last exit status if available
    if st.session_state[rc_key] is not None:
        if st.session_state[rc_key] == 0:
            st.success("Command exited with code 0")
        else:
            st.error(f"Command exited with code {st.session_state[rc_key]}")

    state = st.session_state[state_key]

    if state == "idle":
        if slot.button("Run", key=f"run-button-{id}"):
            st.session_state[state_key] = "running"
            st.session_state[output_key] = ""
            st.session_state[rc_key] = None
            st.rerun()
        return

    if state == "running":
        ansi = re.compile(r"\x1B\[[^A-Za-z]*[A-Za-z]")

        if output:
            with st.expander("Command Output", expanded=True):
                out_box = st.empty()
                out_box.code(st.session_state[output_key], language=None)

                with slot:
                    with st.spinner("Running command..."):
                        proc = subprocess.Popen(
                            ["bash", "-lc", command],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            bufsize=1,
                        )

                        assert proc.stdout is not None
                        for line in proc.stdout:
                            line = ansi.sub("", line)
                            st.session_state[output_key] += line
                            out_box.code(st.session_state[output_key], language=None)

                        st.session_state[rc_key] = proc.wait()
        else:
            with slot:
                with st.spinner("Running command..."):
                    proc = subprocess.Popen(
                        ["bash", "-lc", command],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )

                    assert proc.stdout is not None
                    for line in proc.stdout:
                        # still consume stdout to avoid blocking
                        _ = ansi.sub("", line)

                    st.session_state[rc_key] = proc.wait()

        st.session_state[state_key] = "idle"
        st.rerun()
                
def run_step(description: str, command: str, step_id: int, output: bool = False):
    st.markdown(description)
    run_command(command, step_id, output)

def show_csv(path: Path, title: str) -> bool:
    if os.path.isfile(path):
        with st.expander(title, expanded=True):
            st.dataframe(pl.read_csv(path))
        return True
    return False

BLUE = '#0072B2'
CYAN = '#56B4E9'
GREEN = '#009E73'
PINK = '#CC79A7'
RED = '#D55E00'
ORANGE = '#E69F00'
YELLOW = '#F0E442'
BLACK = '#000000'
WHITE = '#FFFFFF'