// Official React import
import React, { useEffect, useState } from "react";

// Our import
import "./Invitations.css";
import Header from "../../GenericComponents/Header/Header";
import { queries } from "../../../utils/Querier";

const Invitations = () => {
    const [myInvitations, setMyInvitations] = useState([]);

    const handleAcceptInvitation = async (invitation_id) => {
        try {
            const response = await queries.post(`/api/v1/accept_invitation/${invitation_id}`);
            if (response.resp === "success") {
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to accept the invitation.");
        }
    }

    const handleDeclineInvitation = async (invitation_id) => {
        try {
            const response = await queries.delete_query(`/api/v1/delete_invitation/${invitation_id}`);
            if (response.resp === "success") {
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to delete the invitation.");
        }
    }

    useEffect(() => {
        const getMyInvitations = async () => {
            try {
                const response = await queries.get(`/api/v1/my_invitations`);
                if (response.resp === "success") {
                    setMyInvitations(response.msg);
                }
            } catch (error) {
                console.error(error);
            }
        };
        getMyInvitations();
    }, []);

    return (
        <div className="invitations-container">
            <Header />
            <div className="invitations">
                <h1>Invitations</h1>
                {myInvitations.length !== 0 ? (
                    <ul className="invitation-list">
                        {myInvitations.map((invitation, index) => (
                            <li key={index} className="invitation-item">
                                <img
                                    className="invitation-favicon"
                                    src={invitation.favicon}
                                    alt="workspace pic"
                                />
                                <div className="invitation-details">
                                    <p className="invitation-name">{invitation.name}</p>
                                    <div className="invitation-buttons">
                                        <button
                                            className="accept-button"
                                            onClick={() => handleAcceptInvitation(invitation.id)}
                                        >
                                            Accept
                                        </button>
                                        <button
                                            className="decline-button"
                                            onClick={() => handleDeclineInvitation(invitation.id)}
                                        >
                                            Decline
                                        </button>
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="no-invitations">You have no invitation.</p>
                )}
            </div>
        </div>
    )
}

export default Invitations;
