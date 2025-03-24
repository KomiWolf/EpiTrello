// Official React import
import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';

// Our import
import "./Settings.css";
import "../../GenericComponents/Popup.css"
import Header from "../../GenericComponents/Header/Header";
import { queries } from "../../../utils/Querier";
// import { useHeader } from "../../GenericComponents/Header/HeaderContext";

const Settings = () => {
    const navigate = useNavigate();
    const [deleteAccountPopup, setDeleteAccountPopup] = useState(false);

    const handleDeleteAccount = async () => {
        try {
            const response = await queries.delete_query(`/api/v1/user`);

            if (response.resp === "success") {
                localStorage.setItem("isAuthenticated", "false");
                localStorage.removeItem("selectedWorkspace");
                navigate("/auth");
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to delete your account.");
        }
    }

    return (
        <div className="settings-container">
            <Header />
            <div className="settings">
                <h1>Settings</h1>
                <button
                    className="settings-danger-button"
                    onClick={() => setDeleteAccountPopup(true)}
                >
                    Delete your account
                </button>
                {
                    deleteAccountPopup && (
                        <div className="popup-overlay">
                            <div className="popup-content">
                                <h3>Are you sure to delete your account ?</h3>
                                <div className="popup-actions">
                                    <button onClick={handleDeleteAccount}>Yes</button>
                                    <button
                                        onClick={() => setDeleteAccountPopup(false)}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        </div>
                    )
                }
            </div>
        </div>
    )
}

export default Settings;
