import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

import SignUp from './SignUp';
import SignIn from './SignIn';
import ForgotPassword from './ForgotPassword';
import ResetPassword from './ResetPassword';

const AuthEntryPoint = () => {
    const navigate = useNavigate();
    const navigateRef = useRef(navigate);

    useEffect(() => {
        if (localStorage.getItem('isAuthenticated') === "true") {
            navigateRef.current("/menu");
        }
    }, []);

    const [action, setAction] = useState("Sign Up");

    return (
        <div>
            {action === "Sign Up" && <SignUp setAction={setAction} />}
            {action === "Sign In" && <SignIn setAction={setAction} />}
            {action === "Forgot Password" && <ForgotPassword setAction={setAction} />}
            {action === "Reset Password" && <ResetPassword setAction={setAction} />}
        </div>
    );
};

export default AuthEntryPoint;
