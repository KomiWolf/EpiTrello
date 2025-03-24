// Officials React import
import React, { useState, useEffect, useRef } from "react";

// Our import
import "./Auth.css";
import { queries } from "../../../utils/Querier";

import showIcon from "../../../assets/images/show.svg"
import hideIcon from "../../../assets/images/hide.svg"

const ResetPassword = ({ setAction }) => {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [formData, setFormData] = useState({
        email: sessionStorage.getItem("email"),
        code: '',
        password: '',
        confirmPassword: ''
    });
    const emailRef = useRef(formData.email);
    const [errors, setErrors] = useState({});

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSignInClick = async () => {
        try {
            let path = `/api/v1/reset_code/${emailRef.current}`;
            await queries.delete_query(path);
            sessionStorage.removeItem("email");
        } catch (error) {
            console.error(error);
        }
        setAction("Sign In");
    };

    const handleConfirmResetPasswordClick = async () => {
        const newErrors = {};

        if (formData.code.length <= 0) {
            newErrors.code = "Invalid code.";
            setErrors(newErrors);
            return;
        }
        if (formData.password.length < 8) {
            newErrors.password = "Password must be at least 8 characters.";
            setErrors(newErrors);
            return;
        }
        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = "Passwords do not match.";
            setErrors(newErrors);
            return;
        }

        setIsSubmitting(true);
        try {
            const response = await queries.patch("/api/v1/reset_password", formData);

            if (response.resp === "success") {
                sessionStorage.removeItem("email");
                setAction("Sign In");
            }
        } catch (error) {
            alert("Failed to reset password.");
        } finally {
            setIsSubmitting(false);
        }
    };

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setTimeout(() => {
                setErrors({});
            }, 4000);
        }
    }, [errors]);

    useEffect(() => {
        const handleBeforeUnload = async (event) => {
            event.returnValue = "";
            try {
                let path = `/api/v1/reset_code/${emailRef.current}`;
                await queries.delete_query(path);
                sessionStorage.removeItem("email");
            } catch (error) {
                console.error(error);
            }
        };
        window.addEventListener("beforeunload", handleBeforeUnload);
        return () => {
            window.removeEventListener("beforeunload", handleBeforeUnload);
        };
    }, []);

    return (
        <div className="auth-container">
            <div className="auth-form-container">
                <div className="auth-title-container">
                    <p>Reset Password</p>
                </div>

                <p>Verification Code</p>
                <input type="text" name="code" placeholder="Enter the verification code sended by email" value={formData.code} onChange={handleChange} required />
                {errors.code && <p className="error-message">{errors.code}</p>}

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

                <p>Confirm Password</p>
                <div className="password-container">
                    <input
                        type={showConfirmPassword ? "text" : "password"}
                        name="confirmPassword"
                        placeholder="Confirm your password"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        required
                    />
                    <button type="button" className="show-hide-btn" onClick={() => setShowConfirmPassword(!showConfirmPassword)}>
                        <img src={showConfirmPassword ? showIcon : hideIcon} alt="Toggle Confirm Password" />
                    </button>
                </div>
                {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}

                <div className="auth-go-to-container">
                    <span onClick={handleSignInClick}>Return to sign in</span>
                </div>

                <button onClick={handleConfirmResetPasswordClick} className="auth-button">
                    {isSubmitting ? "Submitting..." : "Confirm"}
                </button>
            </div>
        </div>
    );
};

export default ResetPassword;
