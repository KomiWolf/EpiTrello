// Officials React import
import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from 'react-router-dom';

// Our import
import "./Board.css";
import "../../GenericComponents/Popup.css"
import Header from "../../GenericComponents/Header/Header";
import { useHeader } from "../../GenericComponents/Header/HeaderContext";
import { queries } from "../../../utils/Querier";
import List from "./List/List"

// Assets import
import defaultProfileImage from "../../../assets/images/default_pfp.png";

const Board = () => {
    const [loading, setLoading] = useState(true);
    const { boardId } = useParams();
    const { currentSelectedWorkspace, userInfo } = useHeader();
    const navigate = useNavigate();
    const [board, setBoard] = useState({});
    const [memberMe, setMemberMe] = useState({});
    const [membersInfo, setMembersInfo] = useState([]);
    const [clickedMember, setClickedMember] = useState(null);
    const [boardSettingsPopup, setBoardSettingsPopup] = useState(false);
    const boardSettingsPopupRef = useRef(null);
    const [editBoardPopup, setEditBoardPopup] = useState(false);
    const [confirmBoardDeletionPopup, setConfirmBoardDeletionPopup] = useState(false);
    const [createListPopup, setCreateListPopup] = useState(false);
    const [newListName, setNewListName] = useState("");
    let darkerBackground = "";

    const [boardName, setBoardName] = useState("");
    const [boardColor, setBoardColor] = useState("");
    const colors = [
        "#FF6F5E", // Soft red-orange
        "#FFA500", // Standard orange
        "#FFB347", // Orange
        "#FFC07A", // Light Orange
        "#FFD700", // Gold
        "#B8E994", // Pastel green
        "#33FF57", // Bright green
        "#33FF8D", // Turquoise green
        "#33FFDD", // Turquoise blue
        "#33A1FF", // Light blue
        "#3357FF", // Bright blue
        "#8D33FF", // Bright violet
        "#A566FF", // Lavender violet
        "#FF99C8", // Pastel pink
        "#FF6678", // Salmon pink
        "#A2D9FF", // Light pastel blue
        "#40E0D0", // Turquoise
        "#FF82C6", // hot pink
        "#6B7280", // Neutral dark gray
        "#000000", // Black
    ];

    // Set errors for input
    const [errors, setErrors] = useState({});

    const ProfilePopup = ({ member, onClose, setMember }) => {
        return (
            <div
                className="board-page-profile-popup"
                onMouseLeave={() => setMember(null)}
            >
                <div className="board-page-profile-popup-info">
                    {member.favicon === "NULL" ? (
                        <img src={defaultProfileImage} alt={`${member.username}'s profile`} className="popup-image" />
                    ) : (
                        <img src={member.favicon} alt={`${member.username}'s profile`} className="popup-image" />
                    )}
                    <div>
                        <p>{member.username}</p>
                        <p>{member.email}</p>
                    </div>
                </div>
                <button onClick={() => onClose(member.id)}>View Profile</button>
            </div>
        );
    };

    const handleCreateList = async () => {
        const newErrors = {};

        if (!newListName || newListName.length === 0) {
            newErrors.newListName = "The list name must not be empty.";
            setErrors(newErrors);
            return;
        }
        try {
            const response = await queries.post(`/api/v1/board/${board.id}/list`, {
                name: newListName,
            });
            if (response.resp === "success") {
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to create the list.");
        }
    };

    const handleGoToProfile = (memberId) => {
        if (memberId === userInfo.id) {
            navigate("/profile");
        } else {
            navigate(`/profile/${memberId}`);
        }
        setClickedMember(null);
    };

    const toggleBoardSettingsPopup = (event) => {
        event.stopPropagation();
        setClickedMember(null);
        setBoardSettingsPopup(!boardSettingsPopup);
    };

    const openBoardEditPopup = () => {
        setBoardSettingsPopup(false);
        setBoardName(board.name);
        setBoardColor(board.background_color);
        setEditBoardPopup(true);
    };

    const handleEditBoard = async () => {
        const newErrors = {};

        if (!boardName || boardName.length === 0) {
            newErrors.boardName = "The board name must not be empty.";
            setErrors(newErrors);
            return;
        }
        if (!boardColor || boardColor.length === 0) {
            newErrors.boardColor = "You must pick a color for your board.";
            setErrors(newErrors);
            return;
        }
        try {
            const response = await queries.put(`/api/v1/workspace/${currentSelectedWorkspace.id}/board/${board.id}`, {
                name: boardName,
                background_color: boardColor
            });
            if (response.resp === "success") {
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to edit the board.");
        }
    };

    const openBoardDeletionPopup = () => {
        setBoardSettingsPopup(false);
        setConfirmBoardDeletionPopup(true);
    };

    const handleDeleteBoard = async () => {
        try {
            const response = await queries.delete_query(`/api/v1/workspace/${currentSelectedWorkspace.id}/board/${boardId}`);

            if (response.resp === "success") {
                navigate("/menu");
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to delete the board.");
        }
    };

    useEffect(() => {
        const getBoard = async () => {
            try {
                const response = await queries.get(`/api/v1/board/${boardId}`);
                if (response.resp === "success") {
                    setBoard(response.msg);
                }
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        getBoard();
    }, [boardId]);

    useEffect(() => {
        const getMembersInfo = async () => {
            try {
                const memberResponse = await queries.get(`/api/v1/workspace/${currentSelectedWorkspace.id}/members`);
                if (memberResponse.resp === "success") {
                    for (let i = 0; i < memberResponse.msg.length; i++) {
                        if (memberResponse.msg[i].user_id === userInfo.id) {
                            setMemberMe(memberResponse.msg[i]);
                        }
                        const userInfoResponse = await queries.get(`/api/v1/user/${memberResponse.msg[i].user_id}`);
                        if (userInfoResponse.resp === "success") {
                            setMembersInfo((prevMembers) => {
                                const userExists = prevMembers.some(
                                    (member) => member.id === userInfoResponse.msg.id
                                );
                                if (!userExists) {
                                    return [...prevMembers, userInfoResponse.msg];
                                }
                                return prevMembers;
                            });
                        }
                    }
                }
            } catch (error) {
                console.error(error);
            }
        };
        getMembersInfo();
    }, [currentSelectedWorkspace, userInfo]);

    useEffect(() => {
        const handleBoardSettingsClickOutside = (event) => {
            if (boardSettingsPopupRef.current && !boardSettingsPopupRef.current.contains(event.target)) {
                setBoardSettingsPopup(false);
            }
        };
        document.addEventListener("click", handleBoardSettingsClickOutside);
        return () => {
            document.removeEventListener("click", handleBoardSettingsClickOutside);
        };
    }, []);

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setTimeout(() => {
                setErrors({});
            }, 4000);
        }
    }, [errors]);

    const darkenColor = (color, percent) => {
        const num = parseInt(color.slice(1), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = ((num >> 8) & 0x00ff) + amt;
        const B = (num & 0x0000ff) + amt;
        return `#${(
            0x1000000 +
            (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
            (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
            (B < 255 ? (B < 1 ? 0 : B) : 255)
        )
            .toString(16)
            .slice(1)}`;
    };

    if (loading) {
        return;
    }

    if (Object.keys(board).length === 0) {
        return (
            <div className="not-found-container">
                <h1>404 - Board Not Found</h1>
                <p>The board you are looking for doesn't exist or has been removed.</p>
                <button className="go-back-button" onClick={() => navigate("/menu")}>
                    Go Back to Home
                </button>
            </div>
        );
    }

    if (board.background_color === "#000000") {
        darkerBackground = darkenColor(board.background_color, 20);
    } else {
        darkerBackground = darkenColor(board.background_color, -20);
    }

    return (
        <div
            className="board-container"
            style={{
                backgroundColor: board.background_color,
            }}
        >
            <Header />
            <div
                className="board-secondary-bar"
                style={{
                    backgroundColor: darkerBackground,
                }}
            >
                <p>{board.name}</p>
                <div className="board-secondary-bar-right">
                    <section className="board-secondary-bar-right-nav">
                        <div onClick={() => setCreateListPopup(true)}>
                            <p>Create list</p>
                        </div>
                        <div>
                            <p>Activities</p>
                        </div>
                        {
                            (memberMe.admin === 1 || memberMe.board_creation_restriction === 1 || memberMe.board_deletion_restriction === 1) &&
                            <div onClick={toggleBoardSettingsPopup}>
                                <p>Settings</p>
                            </div>
                        }
                    </section>

                    {/* Create List Popup */}
                    {
                        createListPopup && (
                            <div className="popup-overlay">
                                <div className="popup-content">
                                    <h3>Create a new list</h3>
                                    <div>
                                        <label>List Name</label>
                                        <input
                                            type="text"
                                            placeholder="Enter the list name"
                                            value={newListName}
                                            onChange={(e) => setNewListName(e.target.value)}
                                        />
                                        {errors.newListName && <p className="error-message" style={{ color: "red" }}>{errors.newListName}</p>}
                                    </div>
                                    <div className="popup-actions">
                                        <button onClick={handleCreateList}>Create</button>
                                        <button onClick={() => {
                                            setCreateListPopup(false);
                                            setNewListName("");
                                        }}>Cancel</button>
                                    </div>
                                </div>
                            </div>
                        )
                    }

                    {/* Board Settings Popup */}
                    {boardSettingsPopup && (
                        <div className="board-settings-popup" ref={boardSettingsPopupRef}>
                            <ul>
                                {
                                    (memberMe.admin === 1 || memberMe.board_deletion_restriction === 1) && (
                                        <li onClick={openBoardEditPopup}>
                                            Edit Board
                                        </li>
                                    )
                                }
                                {
                                    (memberMe.admin === 1 || memberMe.board_deletion_restriction === 1) && (
                                        <li onClick={openBoardDeletionPopup}>
                                            Delete Board
                                        </li>
                                    )
                                }
                            </ul>
                        </div>
                    )}

                    {/* Edit the board popup */}
                    {
                        editBoardPopup && (
                            <div className="popup-overlay">
                                <div className="popup-content">
                                    <h3>Edit The Board</h3>
                                    <div>
                                        <label>Board Name</label>
                                        <input
                                            type="text"
                                            placeholder="Enter the board name"
                                            value={boardName}
                                            onChange={(e) => setBoardName(e.target.value)}
                                        />
                                        {errors.boardName && <p className="error-message" style={{ color: "red" }}>{errors.boardName}</p>}
                                    </div>
                                    <div>
                                        <label>Board Color</label>
                                        <div className="color-picker">
                                            {colors.map((color) => (
                                                <div
                                                    key={color}
                                                    className={`color-option ${boardColor === color ? 'selected' : ''}`}
                                                    style={{
                                                        backgroundColor: color,
                                                        width: "30px",
                                                        height: "30px",
                                                        borderRadius: "50%",
                                                        margin: "5px",
                                                        cursor: "pointer",
                                                        border: boardColor === color ? "2px solid black" : "none",
                                                    }}
                                                    onClick={() => setBoardColor(color)}
                                                />
                                            ))}
                                            {errors.boardColor && <p className="error-message">{errors.boardColor}</p>}
                                        </div>
                                    </div>
                                    <div className="popup-actions">
                                        <button onClick={handleEditBoard}>Edit</button>
                                        <button onClick={() => setEditBoardPopup(false)}>Cancel</button>
                                    </div>
                                </div>
                            </div>
                        )
                    }

                    {/* Delete the board popup */}
                    {
                        confirmBoardDeletionPopup && (
                            <div className="popup-overlay">
                                <div className="popup-content">
                                    <h3>Are you sure to delete this board ?</h3>
                                    <div className="popup-actions">
                                        <button onClick={handleDeleteBoard}>Yes</button>
                                        <button
                                            onClick={() => setConfirmBoardDeletionPopup(false)}
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )
                    }

                    <hr />
                    <section>
                        {membersInfo.map((member, index) => (
                            <li
                                key={index}
                                onClick={() => setClickedMember(clickedMember === member ? null : member)}
                                className="member-list-item"
                            >
                                {member.favicon === "NULL" ? (
                                    <img src={defaultProfileImage} alt={`${member.username}'s profile`} />
                                ) : (
                                    <img src={member.favicon} alt={`${member.username}'s profile`} />
                                )}
                            </li>
                        ))}
                        {clickedMember && (
                            <ProfilePopup
                                member={clickedMember}
                                onClose={(memberId) => handleGoToProfile(memberId)}
                                setMember={setClickedMember}
                            />
                        )}
                    </section>
                </div>
            </div>
            <List boardId={board.id} />
        </div>
    );
};

export default Board;
