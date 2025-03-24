// Officials React import
import React, { useState, useEffect } from "react";

// Our React import
import "./Auth.css";
import { queries } from "../../../utils/Querier";

const ForgotPassword = ({ setAction }) => {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        email: ''
    });
    const [errors, setErrors] = useState({});

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSignInClick = () => {
        setAction("Sign In");
    };

    const handleConfirmResetPasswordClick = async () => {
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

        setIsSubmitting(true);
        try {
            const response = await queries.post("/api/v1/send_email_verification", formData);

            if (response.resp === "success") {
                sessionStorage.setItem("email", formData.email);
                setAction("Reset Password");
            }
        } catch (error) {
            alert("Failed to send the verification code.");
        } finally {
            setIsSubmitting(false);
        }
    }

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
                    <p>Forgot Password</p>
                </div>
                <p>Email</p>
                <input type="email" name="email" placeholder="Enter your email" value={formData.email} onChange={handleChange} required />
                {errors.email && <p className="error-message">{errors.email}</p>}
                <div className="auth-go-to-container">
                    <span onClick={handleSignInClick}>Return to sign in</span>
                </div>
                <button onClick={handleConfirmResetPasswordClick} className="auth-button">
                    {isSubmitting ? "Submitting..." : "Reset Password"}
                </button>
            </div>
        </div>
    );
};

export default ForgotPassword;
