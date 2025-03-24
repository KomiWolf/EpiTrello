// Official React import
import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from 'react-router-dom';

// Our import
import "./Header.css";
import CreateWorkspacePopup from "./CreateWorkspacePopup";
import { queries } from "../../../utils/Querier";
import { useAuth } from "../../Pages/Auth/AuthContext";
import { useHeader } from "./HeaderContext";

// Assets import
import defaultProfileImage from "../../../assets/images/default_pfp.png";

const Header = () => {
    const { logout } = useAuth();
    const { currentSelectedWorkspace, setCurrentSelectedWorkspace, workspaces, userInfo } = useHeader();
    const profilePopupRef = useRef(null);
    const [isProfilePopupVisible, setProfilePopupVisible] = useState(false);
    const workspacesPopupRef = useRef(null);
    const [isWorkspacePopupVisible, setWorkspacePopupVisible] = useState(false);
    const [profileImage, setProfileImage] = useState(defaultProfileImage);
    const [isCreateWorkspacePopupOpen, setIsCreateWorkspacePopupOpen] = useState(false);
    const navigate = useNavigate();

    const toggleProfilePopup = (event) => {
        event.stopPropagation();
        setProfilePopupVisible(!isProfilePopupVisible);
        if (isWorkspacePopupVisible) {
            setWorkspacePopupVisible(!isWorkspacePopupVisible);
        }
    };

    const toggleWorkspacePopup = (event) => {
        event.stopPropagation();
        setWorkspacePopupVisible(!isWorkspacePopupVisible);
        if (isProfilePopupVisible) {
            setProfilePopupVisible(!isProfilePopupVisible);
        }
    };

    const handleLogoutClick = async () => {
        try {
            const response = await queries.delete_query("/api/v1/logout", {});
            if (response.resp === "success") {
                localStorage.removeItem("selectedWorkspace");
                logout();
            }
        } catch (error) {
            alert("Failed to log you out");
        }
    };

    const handleSelectWorkspaceClick = (workspace) => {
        localStorage.setItem("selectedWorkspace", workspace.name);
        setCurrentSelectedWorkspace(workspace);
        navigate("/menu");
    };

    const handleProfileClick = () => {
        navigate("/profile");
    };

    const handleEpiTrelloClick = () => {
        navigate("/menu");
    };

    const handleSettingsClick = () => {
        navigate("/settings");
    }

    const handleInvitationsClick = () => {
        navigate("/invitations");
    }

    useEffect(() => {
        const handleProfileClickOutside = (event) => {
            if (profilePopupRef.current && !profilePopupRef.current.contains(event.target)) {
                setProfilePopupVisible(false);
            }
        };
        document.addEventListener("click", handleProfileClickOutside);
        return () => {
            document.removeEventListener("click", handleProfileClickOutside);
        };
    }, []);

    useEffect(() => {
        const updateProfileImage = () => {
            if (userInfo.favicon !== "NULL") {
                setProfileImage(userInfo.favicon);
            } else {
                setProfileImage(defaultProfileImage);
            }
        };
        updateProfileImage();
    }, [userInfo]);

    useEffect(() => {
        const handleWorkspaceClickOutside = (event) => {
            if (workspacesPopupRef.current && !workspacesPopupRef.current.contains(event.target)) {
                setWorkspacePopupVisible(false);
            }
        };
        document.addEventListener("click", handleWorkspaceClickOutside);
        return () => {
            document.removeEventListener("click", handleWorkspaceClickOutside);
        };
    }, []);

    return (
        <div className="header-container">
            <div className="left-nav">
                <a href="/menu" onClick={handleEpiTrelloClick}>EpiTrello</a>
                <span onClick={toggleWorkspacePopup}>Workspaces</span>
                {isWorkspacePopupVisible && (
                    <div className="workspaces-popup" ref={workspacesPopupRef} onClick={toggleWorkspacePopup}>
                        {workspaces.length !== 0 ? (
                            <ul>
                                <li>
                                    <p className="list-title">Current Workspace</p>
                                    {Object.keys(currentSelectedWorkspace).length === 0 ? (
                                        <p>None</p>
                                    ) : (
                                        <div className="workspace-container">
                                            <img src={currentSelectedWorkspace.favicon} alt="workspace" />
                                            <p>{currentSelectedWorkspace.name}</p>
                                        </div>
                                    )}
                                </li>
                                <li>
                                    <p className="list-title">Workspaces</p>
                                    <ul className="workspaces-display">
                                        {workspaces.map((workspace) => (
                                            <li key={workspace.id} onClick={() => handleSelectWorkspaceClick(workspace)} className="workspace-container">
                                                <img src={workspace.favicon} alt="workspace" />
                                                <p>{workspace.name}</p>
                                            </li>
                                        ))}
                                    </ul>
                                </li>
                            </ul>
                        ) : (
                            <p>You have no workspace</p>
                        )}
                    </div>
                )}
            </div>
            <div className="profile-container" onClick={toggleProfilePopup}>
                <span>{userInfo.username}</span>
                <img
                    src={profileImage}
                    alt="Profile pic"
                />
                {isProfilePopupVisible && (
                    <div className="profile-popup" ref={profilePopupRef}>
                        <ul>
                            <li onClick={handleProfileClick}>
                                My profile
                            </li>
                            <li onClick={() => setIsCreateWorkspacePopupOpen(true)}>
                                Create a new workspace
                            </li>
                            <li onClick={handleInvitationsClick}>
                                My invitations
                            </li>
                            <li onClick={handleSettingsClick}>
                                Settings
                            </li>
                            <li onClick={handleLogoutClick}>
                                Log out
                            </li>
                        </ul>
                    </div>
                )}
            </div>
            {isCreateWorkspacePopupOpen && <CreateWorkspacePopup setIsPopupOpen={setIsCreateWorkspacePopupOpen} />}
        </div>
    );
};

export default Header;
