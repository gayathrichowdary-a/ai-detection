import os
import base64
import streamlit as st
from auth.database import register_user

def get_signup_image_b64():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(base_dir, ".."))
    possible_paths = [
        os.path.join(root_dir, "assets", "signup_robot.png"),
        os.path.join(root_dir, "assets", "signup_robot.jpg"),
        os.path.join(base_dir, "assets", "signup_robot.png"),
        "assets/signup_robot.png",
        "assets/signup_robot.jpg",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return ""

def signup_page():
    st.markdown("""
        <style>
        .main .block-container {
            max-width: 1050px !important;
            padding-top: 2rem !important;
            padding-bottom: 4rem !important;
        }
        .stTextInput > div > div > input {
            border-radius: 8px !important;
            border: 1px solid #E2E8F0 !important;
            padding: 10px 14px !important;
            font-size: 14px !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 1px #2563EB !important;
        }
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    img_b64 = get_signup_image_b64()

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        img_tag = f'<img src="data:image/png;base64,{img_b64}" style="width: 100%; max-height: 350px; object-fit: cover; border-radius: 16px; margin-bottom: 24px; display: block;" alt="AI Assistant" />' if img_b64 else '<div style="height: 280px; display: flex; align-items: center; justify-content: center; font-size: 72px;">🤖</div>'

        st.markdown(f"""
            <div style="background: linear-gradient(180deg, #021235 0%, #031B4E 50%, #06286E 100%);
                        border-radius: 24px; padding: 32px 28px; color: #FFFFFF;
                        box-shadow: 0 20px 40px -15px rgba(2, 18, 53, 0.4); border: 1px solid rgba(255, 255, 255, 0.1);">
                <div>
                    {img_tag}
                    <h2 style="color: #FFFFFF; font-size: 24px; font-weight: 700; margin: 0 0 8px 0; line-height: 1.3;">
                        Intelligent <span style="color: #38BDF8;">Workspaces</span>
                    </h2>
                    <p style="color: #94A3B8; font-size: 14px; margin: 0 0 16px 0; font-weight: 400;">
                        Enterprise Hybrid RAG Platform
                    </p>
                </div>
                <div style="padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.12); display: flex; gap: 8px; flex-wrap: wrap; font-size: 12px; color: #7DD3FC;">
                    <span>• Vector Embeddings</span>
                    <span>• Automated Routing</span>
                    <span>• Verified Sources</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <div style="margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <div style="background: #2563EB; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; font-weight: bold; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);">
                        ⚡
                    </div>
                    <div>
                        <div style="font-weight: 800; font-size: 18px; color: #0F172A; line-height: 1.1;">Enterprise RAG</div>
                        <div style="font-size: 11px; color: #64748B;">Adaptive Intelligence Knowledge Platform</div>
                    </div>
                </div>
                <h1 style="font-size: 28px; font-weight: 800; color: #0F172A; margin: 12px 0 4px 0;">Create account</h1>
                <p style="font-size: 14px; color: #64748B; margin: 0;">Join the enterprise intelligence knowledge platform</p>
            </div>
        """, unsafe_allow_html=True)

        new_username = st.text_input("Username", key="signup_user", placeholder="Enter your username")
        new_email = st.text_input("Email", key="signup_mail", placeholder="name@company.com")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            new_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="Create password")
        with col_p2:
            confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Confirm password")

        agree_terms = st.checkbox("I agree to the Enterprise Terms of Service and Privacy Policy", value=True, key="signup_terms")

        st.write("")
        if st.button("Create Account", type="primary", use_container_width=True, key="btn_signup_submit"):
            u_clean = new_username.strip()
            e_clean = new_email.strip()
            p_clean = new_pass.strip()
            cp_clean = confirm_pass.strip()

            if not u_clean or not e_clean or not p_clean or not cp_clean:
                st.warning("All fields are required.")
            elif "@" not in e_clean or "." not in e_clean:
                st.error("Please enter a valid email address.")
            elif len(p_clean) < 6:
                st.error("Password must be at least 6 characters long.")
            elif p_clean != cp_clean:
                st.error("Passwords do not match.")
            elif not agree_terms:
                st.warning("Please agree to the Terms of Service to continue.")
            else:
                ok, msg = register_user(u_clean, e_clean, p_clean)
                if ok:
                    st.session_state.reg_success_msg = "Account created successfully! Please sign in."
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(msg)

        st.write("")
        st.markdown('<div style="text-align: center; font-size: 14px; color: #64748B;">Already have an account?</div>', unsafe_allow_html=True)
        if st.button("Sign In", use_container_width=True, key="btn_goto_login"):
            st.session_state.page = "login"
            st.rerun()