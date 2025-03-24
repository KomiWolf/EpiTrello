// Official React import
import React, { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';

// Our import
import "./WorkspaceSettings.css";
import "../../GenericComponents/Popup.css"
import Header from "../../GenericComponents/Header/Header";
import ImageSearch from "../../GenericComponents/ImageSearch/ImageSearch";
import { useHeader } from "../../GenericComponents/Header/HeaderContext";
import { queries } from "../../../utils/Querier";

const WorkspaceSettings = () => {
    const navigate = useNavigate();
    const { currentSelectedWorkspace, userInfo } = useHeader();
    const [workspaceIconPopup, setWorkspaceIconPopup] = useState(false);
    const [uploadOption, setUploadOption] = useState(""); // "local" or "unsplash"
    const [workspaceName, setWorkspaceName] = useState(currentSelectedWorkspace.name);
    const [workspaceDescription, setWorkspaceDescription] = useState(currentSelectedWorkspace.description);
    const [members, setMembers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [memberMe, setMember] = useState({});
    const [invitations, setInvitations] = useState([]);
    const [invitePopup, setInvitePopup] = useState(false);
    const [inviteEmail, setInviteEmail] = useState("");
    const [deleteWorkspacePopup, setDeleteWorkspacePopup] = useState(false);
    const [errors, setErrors] = useState({});

    const handleFileUpload = async (file) => {
        const formData = new FormData();
        formData.append("file", file);
        try {
            const response = await queries.patch(`/api/v1/workspace/${currentSelectedWorkspace.id}`, formData);
            if (response.resp === "success") {
                setWorkspaceIconPopup(false);
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to update the workspace icon.");
        }
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    };

    const handleUnsplashSelect = async (imageUrl) => {
        try {
            const responseImg = await fetch(imageUrl);
            const blob = await responseImg.blob();
            const formData = new FormData();

            formData.append("file", blob, `unsplash_${Date.now()}.jpg`);
            const response = await queries.patch(`/api/v1/workspace/${currentSelectedWorkspace.id}`, formData);
            if (response.resp === "success") {
                setWorkspaceIconPopup(false);
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to update the workspace icon.");
        }
    };

    const handleSave = async () => {
        try {
            const response = await queries.put(`/api/v1/workspace/${currentSelectedWorkspace.id}`, {
                name: workspaceName,
                description: workspaceDescription
            });
            if (response.resp === "success") {
                localStorage.setItem("selectedWorkspace", workspaceName);
                window.location.reload();
            }
        } catch (error) {
            console.error("Failed to save settings:", error);
            alert("Failed to save settings.");
        }
    };

    const handleDeleteWorkspace = async () => {
        try {
            const response = await queries.delete_query(`/api/v1/workspace/${currentSelectedWorkspace.id}`);

            if (response.resp === "success") {
                navigate("/menu");
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to delete the workspace.");
        }
    };

    const handleInviteMember = async () => {
        const newErrors = {};
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        const validateEmail = (email) => {
            return emailRegex.test(email);
        };

        if (!validateEmail(inviteEmail)) {
            newErrors.email = "Invalid email address.";
            setErrors(newErrors);
            return;
        }

        try {
            const response = await queries.post(`/api/v1/workspace/${currentSelectedWorkspace.id}/send_invitation/${inviteEmail}`);
            if (response.resp !== "success") {
                newErrors.email = "The email do not exist or it is already in the workspace.";
                setErrors(newErrors);
            } else {
                window.location.reload();
            }
        } catch (error) {
            newErrors.email = "The email do not exist or it is already in the workspace.";
            setErrors(newErrors);
            console.error(error);
        }
    }

    const handleDeleteInvitation = async (invitation_id) => {
        try {
            const response = await queries.delete_query(`/api/v1/workspace/${currentSelectedWorkspace.id}/delete_invitation/${invitation_id}`);
            if (response.resp === "success") {
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to delete the invitation");
            console.error(error);
        }
    }

    const handleRemoveMember = async (user_id, isQuit) => {
        try {
            const response = await queries.delete_query(`/api/v1/workspace/${currentSelectedWorkspace.id}/delete_member/${user_id}`);
            if (response.resp === "success") {
                if (isQuit === true) {

                }
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to remove the member.");
            console.error(error);
        }
    }

    const handlePermissionChange = async (index, permission, value) => {
        const updatedMembers = [...members];
        try {
            let response = null;

            if (permission === "admin") {
                response = await queries.patch(`/api/v1/workspace/${currentSelectedWorkspace.id}/member_admin/${updatedMembers[index]["user_id"]}`);
            } else if (permission === "board_creation_restriction") {
                response = await queries.patch(`/api/v1/workspace/${currentSelectedWorkspace.id}/member_board_creation/${updatedMembers[index]["user_id"]}`);
            } else if (permission === "board_deletion_restriction") {
                response = await queries.patch(`/api/v1/workspace/${currentSelectedWorkspace.id}/member_board_deletion/${updatedMembers[index]["user_id"]}`);
            } else if (permission === "invitation_restriction") {
                response = await queries.patch(`/api/v1/workspace/${currentSelectedWorkspace.id}/member_invitation/${updatedMembers[index]["user_id"]}`);
            } else {
                return;
            }
            if (response.resp === "success") {
                updatedMembers[index][permission] = value;
                setMembers(updatedMembers);
            }
        } catch (error) {
            alert("Failed to change the right of the user.");
        }
    };

    const UserName = ({ user_id }) => {
        const [username, setUsername] = useState("Loading...");

        useEffect(() => {
            const getUserName = async () => {
                try {
                    const response = await queries.get(`/api/v1/user/${user_id}`);
                    setUsername(response.msg.username || "Unknown User");
                } catch (error) {
                    console.error("Failed to fetch username:", error);
                }
            };
            getUserName();
        }, [user_id]);

        return <span>{username}</span>;
    };

    useEffect(() => {
        const getWorkspaceMembers = async () => {
            try {
                const response = await queries.get(`/api/v1/workspace/${currentSelectedWorkspace.id}/members`);
                setMembers(response.msg);
                for (let i = 0; i < response.msg.length; i++) {
                    if (response.msg[i].user_id === userInfo.id) {
                        setMember(response.msg[i]);
                        return;
                    }
                }
            } catch (error) {
                console.error("Failed to fetch members:", error);
            }
            finally {
                setIsLoading(false);
            };
        };
        getWorkspaceMembers();
    }, [currentSelectedWorkspace.id, userInfo.id]);

    useEffect(() => {
        setWorkspaceName(currentSelectedWorkspace.name);
        setWorkspaceDescription(currentSelectedWorkspace.description);
    }, [currentSelectedWorkspace]);

    useEffect(() => {
        const getWorkspaceInvitations = async () => {
            try {
                const response = await queries.get(`/api/v1/workspace/${currentSelectedWorkspace.id}/invitations`);
                setInvitations(response.msg);
            } catch (error) {
                console.error(error);
            }
        };
        getWorkspaceInvitations();
    }, [currentSelectedWorkspace.id]);

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setTimeout(() => {
                setErrors({});
            }, 4000);
        }
    }, [errors]);

    if (isLoading) {
        return <p>Loading workspace members...</p>;
    }

    return (
        <div className="workspace-settings-container">
            <Header />
            <div className="workspace-settings">
                <h1>Workspace Settings</h1>

                {/* General Informations Section */}
                <section className="workspace-section">
                    <h2>General Information</h2>
                    {
                        userInfo.id === currentSelectedWorkspace.creator_id ? (
                            <div className="workspace-settings-image-container">
                                <img
                                    src={currentSelectedWorkspace.favicon}
                                    alt="Workspace Icon"
                                    style={{
                                        cursor: "pointer"
                                    }}
                                    onClick={() => setWorkspaceIconPopup(true)}
                                />

                                {/* Workspace Icon Popup */}
                                {workspaceIconPopup && (
                                    <div className="popup-overlay">
                                        <div className="popup-content">
                                            <h3>Choose Workspace Icon</h3>
                                            <button onClick={() => setUploadOption("local")}>Upload Local</button>
                                            <button onClick={() => setUploadOption("unsplash")}>Search Unsplash</button>
                                            <button onClick={() => setWorkspaceIconPopup(false)}>Cancel</button>

                                            {/* Local file upload */}
                                            {uploadOption === "local" && (
                                                <div className="local-upload">
                                                    <input
                                                        type="file"
                                                        accept="image/*"
                                                        onChange={handleFileChange}
                                                        style={{ marginTop: "10px" }}
                                                    />
                                                </div>
                                            )}

                                            {/* Unsplash image search */}
                                            {uploadOption === "unsplash" && (
                                                <ImageSearch onImageSelect={handleUnsplashSelect} />
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="workspace-settings-image-container">
                                <img src={currentSelectedWorkspace.favicon} alt="Workspace Icon" />
                            </div>
                        )
                    }
                    <label>
                        Workspace Name:
                        {
                            userInfo.id === currentSelectedWorkspace.creator_id ? (
                                <input
                                    type="text"
                                    value={workspaceName}
                                    placeholder="Enter a name for your workspace"
                                    onChange={(e) => setWorkspaceName(e.target.value)}
                                />
                            ) : (
                                <p>{workspaceName}</p>
                            )
                        }
                    </label>
                    <label>
                        Description:
                        {
                            userInfo.id === currentSelectedWorkspace.creator_id ? (
                                <textarea
                                    value={workspaceDescription}
                                    placeholder="Enter a description for your workspace"
                                    onChange={(e) => setWorkspaceDescription(e.target.value)}
                                />
                            ) : (
                                <p>{workspaceDescription}</p>
                            )
                        }
                    </label>
                </section>

                {/* Manage Member Section */}
                <section className="workspace-section">
                    <h2>Manage Members</h2>
                    <table className="manage-members-table">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Admin</th>
                                <th>Allow Board Creation</th>
                                <th>Allow Board Deletion</th>
                                <th>Allow Invitations</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {members.map((member, index) => (
                                <tr key={index}>
                                    <td><UserName user_id={member.user_id} /></td>
                                    <td>
                                        {
                                            userInfo.id === currentSelectedWorkspace.creator_id && userInfo.id !== member.user_id ? (
                                                <input
                                                    type="checkbox"
                                                    checked={member.admin}
                                                    onChange={(e) =>
                                                        handlePermissionChange(index, "admin", e.target.checked)
                                                    }
                                                />
                                            ) : (
                                                <input
                                                    type="checkbox"
                                                    checked={member.admin}
                                                    onChange={(e) =>
                                                        handlePermissionChange(index, "admin", e.target.checked)
                                                    }
                                                    disabled
                                                />
                                            )
                                        }
                                    </td>
                                    <td>
                                        {
                                            memberMe.admin === 1 && userInfo.id !== member.user_id && member.user_id !== currentSelectedWorkspace.creator_id ? (
                                                <input
                                                    type="checkbox"
                                                    checked={member.board_creation_restriction}
                                                    onChange={(e) =>
                                                        handlePermissionChange(index, "board_creation_restriction", e.target.checked)
                                                    }
                                                />
                                            ) : (
                                                <input
                                                    type="checkbox"
                                                    checked={member.board_creation_restriction}
                                                    onChange={(e) =>
                                                        handlePermissionChange(index, "board_creation_restriction", e.target.checked)
                                                    }
                                                    disabled
                                                />
                                            )
                                        }
                                    </td>
                                    <td>
                                        {
                                            memberMe.admin === 1 && userInfo.id !== member.user_id && member.user_id !== currentSelectedWorkspace.creator_id ? (
                                                <input
                                                    type="checkbox"
                                                    checked={member.board_deletion_restriction}
                                                    onChange={(e) =>
                                                        handlePermissionChange(index, "board_deletion_restriction", e.target.checked)
                                                    }
                                                />
                                            ) : (
                                                <input
                                                    type="checkbox"
                                                    checked={member.board_deletion_restriction}
                                                    onChange={(e) =>
                                                        handlePermissionChange(index, "board_deletion_restriction", e.target.checked)
                                                    }
                                                    disabled
                                                />
                                            )
                                        }
                                    </td>
                                    <td>
                                        {
                                            memberMe.admin === 1 && userInfo.id !== member.user_id && member.user_id !== currentSelectedWorkspace.creator_id ? (
                                                <input
                                                    type="checkbox"
                                                    checked={member.invitation_restriction}
                                                    onChange={(e) =>
                                                        handlePermissionChange(index, "invitation_restriction", e.target.checked)
                                                    }
                                                />
                                            ) : (
                                                <input
                                                    type="checkbox"
                                                    checked={member.invitation_restriction}
                                                    onChange={(e) =>
                                                        handlePermissionChange(index, "invitation_restriction", e.target.checked)
                                                    }
                                                    disabled
                                                />
                                            )
                                        }
                                    </td>
                                    <td>
                                        <div className="manage-members-actions">
                                            {
                                                userInfo.id === currentSelectedWorkspace.creator_id && userInfo.id !== member.user_id ? (
                                                    <button
                                                        className="remove"
                                                        onClick={() => handleRemoveMember(member.user_id, false)}
                                                    >
                                                        Remove
                                                    </button>
                                                ) : userInfo.id !== currentSelectedWorkspace.creator_id && userInfo.id === member.user_id ? (
                                                    <button
                                                        className="remove"
                                                        onClick={() => handleRemoveMember(member.user_id, true)}
                                                    >
                                                        Quit
                                                    </button>
                                                ) : (
                                                    <p>No actions</p>
                                                )
                                            }
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {
                        (memberMe.admin === 1 || memberMe.invitation_restriction === 1) && (
                            <button
                                className="invite-button"
                                onClick={() => setInvitePopup(true)}
                            >
                                Invite Member
                            </button>
                        )
                    }
                    {
                        invitePopup && (
                            <div className="popup-overlay">
                                <div className="popup-content">
                                    <h3>Invite a New Member</h3>
                                    <input
                                        type="text"
                                        placeholder="Enter an email"
                                        value={inviteEmail}
                                        onChange={(e) => setInviteEmail(e.target.value)}
                                    />
                                    {errors.email && <p className="error-message">{errors.email}</p>}
                                    <div className="popup-actions">
                                        <button onClick={handleInviteMember}>Invite</button>
                                        <button
                                            onClick={() => {
                                                setInviteEmail("");
                                                setInvitePopup(false);
                                            }}
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )
                    }
                </section>

                {/* Invitations section */}
                <section className="workspace-section">
                    <h2>Invitations</h2>
                    {
                        invitations.length !== 0 ? (
                            invitations.map((invitation, index) => (
                                <li key={index}>
                                    <div className="invitation-profile-container">
                                        <img src={invitation.favicon} alt="user icon" />
                                        <div className="invitation-profile-info">
                                            <p>{invitation.username}</p>
                                            <p>{invitation.email}</p>
                                        </div>
                                    </div>
                                    {
                                        (memberMe.admin === 1 || memberMe.invitation_restriction === 1) && (
                                            <button
                                                className="danger-button"
                                                onClick={() => handleDeleteInvitation(invitation.id)}
                                            >
                                                Delete invitation
                                            </button>
                                        )
                                    }
                                </li>
                            ))
                        ) : (
                            <p>No user invited in the workspace</p>
                        )
                    }
                </section>

                {/* Advanced Settings Section */}
                {
                    userInfo.id === currentSelectedWorkspace.creator_id && (
                        <section className="workspace-section danger-zone">
                            <h2>Advanced Settings</h2>
                            <button className="danger-button" onClick={() => setDeleteWorkspacePopup(true)}>
                                Delete Workspace
                            </button>
                            {
                                deleteWorkspacePopup && (
                                    <div className="popup-overlay">
                                        <div className="popup-content">
                                            <h3>Are you sure to delete this workspace ?</h3>
                                            <div className="popup-actions">
                                                <button onClick={handleDeleteWorkspace}>Yes</button>
                                                <button
                                                    onClick={() => setDeleteWorkspacePopup(false)}
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )
                            }
                        </section>
                    )
                }

                {/* Save button */}
                {
                    memberMe.admin === 1 && (
                        <button className="save-button" onClick={handleSave}>
                            Save Changes
                        </button>
                    )
                }
            </div>
        </div>
    );
};

export default WorkspaceSettings;
