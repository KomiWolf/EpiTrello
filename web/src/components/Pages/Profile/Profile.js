// Official React import
import React, { useState, useEffect } from "react";

// Our import
import "./Profile.css";
import "../../GenericComponents/Popup.css"
import Header from "../../GenericComponents/Header/Header";
import { useHeader } from "../../GenericComponents/Header/HeaderContext";
import { queries } from "../../../utils/Querier";
import ImageSearch from "../../GenericComponents/ImageSearch/ImageSearch";

// Assets import
import defaultProfileImage from "../../../assets/images/default_pfp.png";

const Profile = () => {
    const { userInfo } = useHeader();
    const [profileImage, setProfileImage] = useState(defaultProfileImage);
    const [showEditPhotoPopup, setShowEditPhotoPopup] = useState(false);
    const [uploadOption, setUploadOption] = useState(""); // "local" or "unsplash"
    const [showEditProfile, setShowEditProfile] = useState(false);
    const [showChangePassword, setShowChangePassword] = useState(false);

    // Profile state for input
    const [username, setUsername] = useState(userInfo.username);
    const [email, setEmail] = useState(userInfo.email);
    const [bio, setBio] = useState(userInfo.bio);

    // Change password state
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    // Set errors for input
    const [errors, setErrors] = useState({});

    const handleFileUpload = async (file) => {
        const formData = new FormData();
        formData.append("file", file);
        try {
            const response = await queries.post("/api/v1/update_profile_photo", formData);
            if (response.resp === "success") {
                setShowEditPhotoPopup(false);
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to update profile picture.");
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
            const response = await queries.post("/api/v1/update_profile_photo", formData);
            if (response.resp === "success") {
                setShowEditPhotoPopup(false);
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to update profile picture.");
        }
    };

    const handleProfileUpdate = async () => {
        const newErrors = {};
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        const validateEmail = (email) => {
            return emailRegex.test(email);
        };

        if (username.length === 0) {
            newErrors.username = "The username cannot be empty."
            setErrors(newErrors);
            return;
        };

        if (!validateEmail(email)) {
            newErrors.email = "Invalid email address.";
            setErrors(newErrors);
            return;
        }
        try {
            const response = await queries.put("/api/v1/user", {
                username,
                email,
                bio
            });
            if (response.resp === "success") {
                setShowEditProfile(false);
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to update profile.");
        }
    };

    const handleChangePassword = async () => {
        const newErrors = {};

        if (newPassword.length < 8) {
            newErrors.password = "Password must be at least 8 characters.";
            setErrors(newErrors);
            return;
        }
        if (newPassword !== confirmPassword) {
            newErrors.confirmPassword = "Passwords do not match.";
            setErrors(newErrors);
            return;
        }

        try {
            const response = await queries.patch("/api/v1/user", {
                password: newPassword,
            });
            if (response.resp === "success") {
                setShowChangePassword(false);
            }
        } catch (error) {
            console.error("Error changing password:", error);
            alert("Failed to change password.");
        }
    };

    useEffect(() => {
        const updateProfileImage = () => {
            if (userInfo.favicon !== "NULL" && userInfo.favicon != null) {
                setProfileImage(userInfo.favicon);
            }
        };
        updateProfileImage();
    }, [userInfo]);

    useEffect(() => {
        setUsername(userInfo.username);
        setEmail(userInfo.email);
        setBio(userInfo.bio);
    }, [userInfo, showEditProfile]);

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setTimeout(() => {
                setErrors({});
            }, 4000);
        }
    }, [errors]);

    return (
        <div>
            <Header />
            <div className="profile-page-container">
                <div className="profile-info-container">
                    <div className="profile-title-container">
                        <p>My Profile</p>
                    </div>
                    <div className="profile-photo-container">
                        <img
                            src={profileImage}
                            alt="Profile"
                            className="profile-photo"
                            onClick={() => setShowEditPhotoPopup(true)}
                        />
                    </div>
                    <div className="profile-field">
                        <span>Username:</span>
                        <p>{userInfo.username || "N/A"}</p>
                    </div>
                    <div className="profile-field">
                        <span>Email:</span>
                        <p>{userInfo.email || "N/A"}</p>
                    </div>
                    <div className="profile-field">
                        <span>Bio:</span>
                        <p>{userInfo.bio || "No bio provided."}</p>
                    </div>
                    <div className="profile-button-container">
                        <button className="profile-button" onClick={() => setShowEditProfile(true)}>Edit Profile</button>
                        <button className="profile-button" onClick={() => setShowChangePassword(true)}>Change Password</button>
                    </div>
                </div>
            </div>

            {/* Popup for upload options */}
            {showEditPhotoPopup && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <h3>Choose Profile Picture</h3>
                        <button onClick={() => setUploadOption("local")}>Upload Local</button>
                        <button onClick={() => setUploadOption("unsplash")}>Search Unsplash</button>
                        <button onClick={() => setShowEditPhotoPopup(false)}>Cancel</button>

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

            {/* Modal pour l'édition du profil */}
            {showEditProfile && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <h3>Edit Profile</h3>
                        <label>
                            Username:
                            <input
                                type="text"
                                value={username}
                                placeholder="Enter a new username"
                                onChange={(e) => setUsername(e.target.value)}
                            />
                            {errors.username && <p className="error-message">{errors.username}</p>}
                        </label>
                        <label>
                            Email:
                            <input
                                type="email"
                                value={email}
                                placeholder="Enter a new email"
                                onChange={(e) => setEmail(e.target.value)}
                            />
                            {errors.email && <p className="error-message">{errors.email}</p>}
                        </label>
                        <label>
                            Bio:
                            <textarea
                                value={bio}
                                placeholder="Enter a new bio"
                                onChange={(e) => {
                                    setBio(e.target.value)
                                }}
                                onInput={(e) => {
                                    e.target.style.height = "auto";
                                    e.target.style.height = `${e.target.scrollHeight}px`;
                                }}
                            />
                        </label>
                        <button onClick={() => handleProfileUpdate()}>Save Changes</button>
                        <button onClick={() => setShowEditProfile(false)}>Cancel</button>
                    </div>
                </div>
            )}

            {/* Modal pour le changement de mot de passe */}
            {showChangePassword && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <h3>Change Password</h3>
                        <label>
                            New Password:
                            <input
                                type="password"
                                value={newPassword}
                                placeholder="Enter a new password"
                                onChange={(e) => setNewPassword(e.target.value)}
                            />
                            {errors.password && <p className="error-message">{errors.password}</p>}
                        </label>
                        <label>
                            Confirm New Password:
                            <input
                                type="password"
                                value={confirmPassword}
                                placeholder="Confirm your new password"
                                onChange={(e) => setConfirmPassword(e.target.value)}
                            />
                            {errors.confirmPassword && <p className="error-message">{errors.confirmPassword}</p>}
                        </label>
                        <button onClick={() => handleChangePassword()}>Change Password</button>
                        <button onClick={() => setShowChangePassword(false)}>Cancel</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Profile;
