// Officials React import
import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';

// Our import
import "./Menu.css";
import "../../GenericComponents/Popup.css"
import Header from "../../GenericComponents/Header/Header";
import { useHeader } from "../../GenericComponents/Header/HeaderContext";
import { queries } from "../../../utils/Querier";

const Menu = () => {
    const navigate = useNavigate();
    const { currentSelectedWorkspace, userInfo } = useHeader();
    const [boards, setBoards] = useState([]);
    const [memberMe, setMemberMe] = useState({});
    const [createBoardPopup, setCreateBoardPopup] = useState(false);

    // For Board creation
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

    const handleWorkspaceSettingsButton = () => {
        navigate('/workspace-settings');
    };

    const handleCreateBoard = async () => {
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
            const response = await queries.post(`/api/v1/workspace/${currentSelectedWorkspace.id}/board`, {
                name: boardName,
                background_color: boardColor
            });
            if (response.resp === "success") {
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to create a new board.");
        }
    };

    const handleCancelBoardCreation = () => {
        setBoardName("");
        setBoardColor("");
        setCreateBoardPopup(false);
    };

    const handleGoToBoardPage = (board_id) => {
        navigate(`/board/${board_id}`);
    }

    useEffect(() => {
        const getWorkspaceBoards = async () => {
            if (Object.keys(currentSelectedWorkspace).length === 0) {
                return;
            }
            try {
                const path = `/api/v1/workspace/${currentSelectedWorkspace.id}/boards`;
                const response = await queries.get(path);
                if (response.resp === "success") {
                    setBoards(response.msg);
                }
            } catch (error) {
                setBoards([]);
            }
        }
        getWorkspaceBoards();
    }, [currentSelectedWorkspace]);

    useEffect(() => {
        if (Object.keys(currentSelectedWorkspace).length === 0) {
            return;
        }
        const getMember = async () => {
            try {
                const response = await queries.get(`/api/v1/workspace/${currentSelectedWorkspace.id}/member/${userInfo.id}`);
                if (response.resp === "success") {
                    setMemberMe(response.msg);
                }
            } catch (error) {
                console.error(error);
            }
        };
        getMember();
    }, [currentSelectedWorkspace, userInfo]);

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setTimeout(() => {
                setErrors({});
            }, 4000);
        }
    }, [errors]);

    return (
        <div className="menu-container">
            <Header />
            {Object.keys(currentSelectedWorkspace).length !== 0 && (
                <div className="button-option">
                    {memberMe.board_creation_restriction === 1 && (
                        <button onClick={() => setCreateBoardPopup(true)}>Create Board</button>
                    )}
                    {createBoardPopup && (
                        <div className="popup-overlay">
                            <div className="popup-content">
                                <h3>Create a New Board</h3>
                                <div>
                                    <label>Board Name</label>
                                    <input
                                        type="text"
                                        placeholder="Enter the board name"
                                        value={boardName}
                                        onChange={(e) => setBoardName(e.target.value)}
                                    />
                                    {errors.boardName && <p className="error-message">{errors.boardName}</p>}
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
                                    <button onClick={handleCreateBoard}>Create</button>
                                    <button onClick={handleCancelBoardCreation}>Cancel</button>
                                </div>
                            </div>
                        </div>
                    )}
                    <button onClick={handleWorkspaceSettingsButton}>Workspace settings</button>
                </div>
            )}
            <div className="menu-content">
                {
                    Object.keys(currentSelectedWorkspace).length === 0 ? (
                        <div className="workspace-placeholder">
                            <h3 className="workspace-title">Choose a workspace</h3>
                            <p>Select a workspace from the menu above to view its boards and tasks.</p>
                        </div>
                    ) : (
                        <div className="workspace-details">
                            <div className="workspace-header">
                                <div className="workspace-info">
                                    <img src={currentSelectedWorkspace.favicon} alt="Workspace Icon" className="workspace-icon" />
                                    <h3 className="workspace-title">{currentSelectedWorkspace.name}</h3>
                                </div>
                                <p className="workspace-description">{currentSelectedWorkspace.description}</p>
                            </div>
                            <div className="boards-container">
                                {boards && boards.length > 0 ? (
                                    boards.map((board, index) => (
                                        <div
                                            key={index}
                                            className="board-item"
                                            style={{
                                                backgroundColor: board.background_color
                                            }}
                                            onClick={() => handleGoToBoardPage(board.id)}
                                        >
                                            <h4 className="board-title">{board.name}</h4>
                                        </div>
                                    ))
                                ) : (
                                    <p className="no-boards-message">No boards found in this workspace.</p>
                                )}
                            </div>
                        </div>
                    )
                }
            </div>
        </div >
    )
};

export default Menu;
