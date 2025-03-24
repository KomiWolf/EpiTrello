// Officials React import
import React, { useState, useEffect } from "react";

// Our import
import { useAuth } from './AuthContext';
import "./Auth.css";
import { queries } from "../../../utils/Querier";

import googleIcon from "../../../assets/images/googleicon.svg"
import githubIcon from "../../../assets/images/githubicon.svg"
import showIcon from "../../../assets/images/show.svg"
import hideIcon from "../../../assets/images/hide.svg"

const SignIn = ({ setAction }) => {
    const { login } = useAuth();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });
    const [errors, setErrors] = useState({});

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSignUpClick = () => {
        setAction("Sign Up");
    };

    const handleForgotPasswordClick = () => {
        setAction("Forgot Password");
    };

    const handleConfirmSignInClick = async () => {
        const newErrors = {};
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        const validateEmail = (email) => {
            return emailRegex.test(email);
        };

        if (!validateEmail(formData.email)) {
            newErrors.email = "Invalid email address.";
            setErrors(newErrors);
            return;
        }
        if (formData.password.length < 8) {
            newErrors.password = "Password must be at least 8 characters.";
            setErrors(newErrors);
            return;
        }

        setIsSubmitting(true);
        try {
            const response = await queries.post("/api/v1/login", formData);

            if (response.resp === "success") {
                login();
            }
        } catch (error) {
            alert("Failed to login.");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleOAuthLogin = async (provider) => {
        try {
            const response = await queries.post(`/api/v1/oauth/login`, { provider });
            if (response.resp === "success") {
                let url = response["authorization_url"];
                url = decodeURIComponent(url);
                window.location.href = url;
            }
        } catch (error) {
            alert(`Failed to log in with ${provider}.`);
        }
    };

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setTimeout(() => {
                setErrors({});
            }, 4000);
        }
    }, [errors]);

    return (
        <div className="auth-container">
            <div className="auth-form-container">
                <div className="auth-title-container">
                    <p>Sign In</p>
                </div>

                <p>Email</p>
                <input type="email" name="email" placeholder="Enter your email" value={formData.email} onChange={handleChange} required />
                {errors.email && <p className="error-message">{errors.email}</p>}

                <p>Password</p>
                <div className="password-container">
                    <input
                        type={showPassword ? "text" : "password"}
                        name="password"
                        placeholder="Enter your password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                    <button type="button" className="show-hide-btn" onClick={() => setShowPassword(!showPassword)}>
                        <img src={showPassword ? showIcon : hideIcon} alt="Toggle Password" />
                    </button>
                </div>
                {errors.password && <p className="error-message">{errors.password}</p>}

                <div className="auth-go-to-container">
                    <p>Forgot your password ?</p>
                    <span onClick={handleForgotPasswordClick}>Click here</span>
                </div>

                <div className="auth-go-to-container" style={{ marginTop: "-8px" }}>
                    <p>Don't have an account ?</p>
                    <span onClick={handleSignUpClick}>Click here</span>
                </div>

                <button onClick={handleConfirmSignInClick} className="auth-button">
                    {isSubmitting ? "Submitting..." : "Confirm"}
                </button>

                {/* OAuth buttons */}
                <div className="oauth-buttons-container">
                    <p className="oauth-text">Or sign in with</p>
                    <button className="oauth-button google" onClick={() => handleOAuthLogin("google")}>
                        <img src={googleIcon} alt="Google" className="oauth-icon" />
                        Continue with Google
                    </button>
                    <button className="oauth-button github" onClick={() => handleOAuthLogin("github")}>
                        <img src={githubIcon} alt="GitHub" className="oauth-icon" />
                        Continue with GitHub
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SignIn;
