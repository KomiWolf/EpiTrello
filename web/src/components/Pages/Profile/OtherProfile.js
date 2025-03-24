// Official React import
import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

// Our import
import "./Profile.css";
import "../../GenericComponents/Popup.css";
import Header from "../../GenericComponents/Header/Header";
import { queries } from "../../../utils/Querier";

// Assets import
import defaultProfileImage from "../../../assets/images/default_pfp.png";

const OtherProfile = () => {
    const { userId } = useParams();
    const [userInfo, setUserInfo] = useState({});
    const [profileImage, setProfileImage] = useState(defaultProfileImage);

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const response = await queries.get(`/api/v1/user/${userId}`);
                if (response.resp === "success") {
                    setUserInfo(response.msg);
                    if (response.msg.favicon !== "NULL" && response.msg.favicon) {
                        setProfileImage(response.msg.favicon);
                    }
                }
            } catch (error) {
                console.error("Failed to fetch user information:", error);
            }
        };
        fetchUserInfo();
    }, [userId]);

    return (
        <div>
            <Header />
            <div className="profile-page-container">
                <div className="profile-info-container">
                    <div className="profile-title-container">
                        <p>{userInfo.username ? `${userInfo.username}'s Profile` : "User Profile"}</p>
                    </div>
                    <div className="profile-photo-container">
                        <img
                            src={profileImage}
                            alt="Profile"
                            className="profile-photo"
                            style={{ cursor: "auto" }}
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
                </div>
            </div>
        </div>
    );
};

export default OtherProfile;
