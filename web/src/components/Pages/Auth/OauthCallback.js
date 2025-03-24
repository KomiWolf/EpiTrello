// Officials React import
import React, { useEffect, useRef } from "react";
import { useNavigate } from 'react-router-dom';

// Our import
import { useAuth } from './AuthContext';
import "./Auth.css";
import { queries } from "../../../utils/Querier";

const OauthCallback = () => {
    const { login } = useAuth();
    const navigate = useNavigate();
    const navigateRef = useRef(navigate);
    const loginRef = useRef(login);

    useEffect(() => {
        const handleProviderCallback = async () => {
            const urlParams = new URLSearchParams(window.location.href.split('?')[1]);
            const code = urlParams.get("code");
            if (code) {
                let path = "/api/v1/oauth/callback?";
                path += window.location.href.split('?')[1];
                try {
                    const response = await queries.post(path);
                    if (response.resp === "success") {
                        loginRef.current();
                    }
                } catch (error) {
                    alert("The oauth connexion has failed.");
                    navigateRef.current("/auth");
                }
            }
        };
        handleProviderCallback();
    }, []);

    return (
        <>
            <p>Authenticating...</p>
        </>
    );
};

export default OauthCallback;
