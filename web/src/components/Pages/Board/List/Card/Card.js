// Official React import
import React, { useState, useEffect } from "react";

// Our import
import "./Card.css";
import "../../../../GenericComponents/Popup.css";
import { queries } from "../../../../../utils/Querier";
import { useHeader } from "../../../../GenericComponents/Header/HeaderContext";

// Assets import
import defaultProfileImage from "../../../../../assets/images/default_pfp.png";

export const DropIndicator = ({ beforeId, list }) => {
    return (
        <div
            data-before={beforeId || "-1"}
            data-column-id={list.id}
            className="drop-indicator"
        />
    )
}

const LabelsPopup = ({ cardId, labels, setLabels }) => {
    // For label creation
    const [createLabelPopup, setCreateLabelPopup] = useState(false);
    const [modifyLabelPopup, setModifyLabelPopup] = useState(false);
    const [savedLabelId, setSavedLabelId] = useState(null);
    const [labelTitle, setLabelTitle] = useState("");
    const [labelColor, setLabelColor] = useState("");
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

    const handleCreateLabel = async () => {
        const newErrors = {};

        if (!labelTitle || labelTitle.length === 0) {
            newErrors.labelTitle = "The label title must not be empty.";
            setErrors(newErrors);
            return;
        }
        if (!labelColor || labelColor.length === 0) {
            newErrors.labelColor = "You must pick a color for your label.";
            setErrors(newErrors);
            return;
        }
        try {
            const response = await queries.post(`/api/v1/card/${cardId}/label`, {
                title: labelTitle,
                color: labelColor
            });
            if (response.resp === "success") {
                const getResponse = await queries.get(`/api/v1/card/${cardId}/labels`);
                if (getResponse.resp === "success") {
                    setLabels(getResponse.msg);
                    setLabelTitle("");
                    setLabelColor("");
                    setCreateLabelPopup(false);
                }
            }
        } catch (error) {
            alert("Failed to create a new label.");
        }
    };

    const handleCancelLabelCreation = () => {
        setLabelTitle("");
        setLabelColor("");
        setCreateLabelPopup(false);
    };

    const handleModifyLabel = async () => {
        const newErrors = {};

        if (!labelTitle || labelTitle.length === 0) {
            newErrors.labelTitle = "The label title must not be empty.";
            setErrors(newErrors);
            return;
        }
        if (!labelColor || labelColor.length === 0) {
            newErrors.labelColor = "You must pick a color for your label.";
            setErrors(newErrors);
            return;
        }
        try {
            const response = await queries.put(`/api/v1/card/${cardId}/label/${savedLabelId}`, {
                title: labelTitle,
                color: labelColor
            });
            if (response.resp === "success") {
                const getResponse = await queries.get(`/api/v1/card/${cardId}/labels`);
                if (getResponse.resp === "success") {
                    setLabels(getResponse.msg);
                    setLabelTitle("");
                    setLabelColor("");
                    setSavedLabelId(null);
                    setModifyLabelPopup(false);
                }
            }
        } catch (error) {
            alert("Failed to create a new label.");
        }
    };

    const handleCancelLabelModification = () => {
        setLabelTitle("");
        setLabelColor("");
        setModifyLabelPopup(false);
    };

    const handleDeleteLabel = async (labelId) => {
        try {
            const response = await queries.delete_query(`/api/v1/card/${cardId}/label/${labelId}`);
            if (response.resp === "success") {
                setLabels(labels.filter(label => label.id !== labelId));
            }
        } catch (error) {
            console.error(error);
        }
    }

    return (
        <>
            <div style={{ padding: "12px" }}>
                <h4 style={{ marginBottom: "10px", fontSize: "16px", color: "#333" }}>Labels</h4>

                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "10px" }}>
                    {labels.map((label) => (
                        <button
                            onClick={() => {
                                setSavedLabelId(label.id);
                                setLabelTitle(label.title);
                                setLabelColor(label.color);
                                setModifyLabelPopup(true);
                            }}
                            key={label.id}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                backgroundColor: "#f4f4f4",
                                border: "1px solid #ddd",
                                borderRadius: "20px",
                                padding: "6px 12px",
                                cursor: "pointer",
                                transition: "0.2s",
                            }}
                            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#e0e0e0"}
                            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#f4f4f4"}
                        >
                            <span
                                style={{
                                    backgroundColor: label.color,
                                    width: 12,
                                    height: 12,
                                    borderRadius: "50%",
                                    display: "inline-block",
                                    marginRight: 8
                                }}
                            />
                            {label.title}
                            <button
                                onClick={(event) => {
                                    event.stopPropagation();
                                    handleDeleteLabel(label.id)
                                }}
                                style={{
                                    background: "transparent",
                                    border: "none",
                                    cursor: "pointer",
                                    marginLeft: "10px",
                                    fontSize: "14px",
                                    color: "#888",
                                    transition: "0.2s"
                                }}
                                onMouseOver={(e) => e.currentTarget.style.color = "#d9534f"}
                                onMouseOut={(e) => e.currentTarget.style.color = "#888"}
                            >
                                ✖
                            </button>
                        </button>
                    ))}
                </div>
                <button className="action-button" onClick={() => setCreateLabelPopup(true)}>+ Add a label</button>
            </div>

            {createLabelPopup && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <h3>Create a New Label</h3>
                        <div>
                            <label>Label Title</label>
                            <input
                                type="text"
                                placeholder="Enter the label title"
                                value={labelTitle}
                                onChange={(e) => setLabelTitle(e.target.value)}
                            />
                            {errors.labelTitle && <p className="error-message">{errors.labelTitle}</p>}
                        </div>
                        <div>
                            <label>Label Color</label>
                            <div className="color-picker">
                                {colors.map((color) => (
                                    <div
                                        key={color}
                                        className={`color-option ${labelColor === color ? 'selected' : ''}`}
                                        style={{
                                            backgroundColor: color,
                                            width: "30px",
                                            height: "30px",
                                            borderRadius: "50%",
                                            margin: "5px",
                                            cursor: "pointer",
                                            border: labelColor === color ? "2px solid black" : "none",
                                        }}
                                        onClick={() => setLabelColor(color)}
                                    />
                                ))}
                                {errors.labelColor && <p className="error-message">{errors.labelColor}</p>}
                            </div>
                        </div>
                        <div className="popup-actions">
                            <button onClick={handleCreateLabel}>Create</button>
                            <button onClick={handleCancelLabelCreation}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {modifyLabelPopup && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <h3>Modify a Label</h3>
                        <div>
                            <label>Label Title</label>
                            <input
                                type="text"
                                placeholder="Enter the label title"
                                value={labelTitle}
                                onChange={(e) => setLabelTitle(e.target.value)}
                            />
                            {errors.labelTitle && <p className="error-message">{errors.labelTitle}</p>}
                        </div>
                        <div>
                            <label>Label Color</label>
                            <div className="color-picker">
                                {colors.map((color) => (
                                    <div
                                        key={color}
                                        className={`color-option ${labelColor === color ? 'selected' : ''}`}
                                        style={{
                                            backgroundColor: color,
                                            width: "30px",
                                            height: "30px",
                                            borderRadius: "50%",
                                            margin: "5px",
                                            cursor: "pointer",
                                            border: labelColor === color ? "2px solid black" : "none",
                                        }}
                                        onClick={() => setLabelColor(color)}
                                    />
                                ))}
                                {errors.labelColor && <p className="error-message">{errors.labelColor}</p>}
                            </div>
                        </div>
                        <div className="popup-actions">
                            <button onClick={handleModifyLabel}>Modify</button>
                            <button onClick={handleCancelLabelModification}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

const DisplayUser = ({ user, onClick }) => {
    const [profileImage, setProfileImage] = useState(defaultProfileImage);

    useEffect(() => {
        const updateProfileImage = () => {
            if (user.favicon !== "NULL") {
                setProfileImage(user.favicon);
            } else {
                setProfileImage(defaultProfileImage);
            }
        };
        updateProfileImage();
    }, [user]);

    return (
        <div className="assignees-popup-user-info" onClick={onClick}>
            <img src={profileImage} alt={`${user.username}'s profile pic`} />
            <p>{user.username}</p>
        </div>
    )
};

const AssignMembersPopup = ({ cardId, assignees, setAssignees }) => {
    const { currentSelectedWorkspace } = useHeader();
    const [boardMembers, setBoardMembers] = useState([]);

    const assignMember = async (member) => {
        try {
            const response = await queries.post(`/api/v1/card/${cardId}/assignee`, {
                user_id: member.id.toString(),
                workspace_id: currentSelectedWorkspace.id.toString()
            });
            if (response.resp === "success") {
                setAssignees((prevAssignees) =>
                    prevAssignees.some((user) => user.id === member.id)
                        ? prevAssignees.filter((user) => user.id !== member.id)
                        : [...prevAssignees, member]
                );
                setBoardMembers((prevBoardMembers) => prevBoardMembers.filter((user) => user.id !== member.id));
            }
        } catch (error) {
            console.error("Error toggling assignee:", error);
        }
    };

    const deleteAssignee = async (assignee) => {
        try {
            const response = await queries.delete_query(`/api/v1/card/${cardId}/assignee/${assignee.id}`);
            if (response.resp === "success") {
                setAssignees((prevAssignees) => prevAssignees.filter((user) => user.id !== assignee.id));
                setBoardMembers((prevBoardMembers) => [...prevBoardMembers, assignee]);
            }
        } catch (error) {
            console.error(error);
        }
    }

    useEffect(() => {
        const getBoardMembers = async () => {
            try {
                const getMembersResponse = await queries.get(`/api/v1/workspace/${currentSelectedWorkspace.id}/members`);

                if (getMembersResponse.resp === "success") {
                    const members = getMembersResponse.msg;
                    const userRequests = members.map(member =>
                        queries.get(`/api/v1/user/${member.user_id}`)
                    );
                    const usersResponses = await Promise.all(userRequests);
                    const validUsers = usersResponses
                        .filter(userRes => userRes.resp === "success")
                        .map(userRes => userRes.msg);
                    const filteredBoardMembers = validUsers.filter(
                        user => !assignees.some(assignee => assignee.id === user.id)
                    );

                    setBoardMembers(filteredBoardMembers);
                }
            } catch (error) {
                console.error(error);
            }
        };
        getBoardMembers();
    }, [currentSelectedWorkspace, assignees]);

    return (
        <div>
            <h4>Assigned members</h4>
            <div>
                {assignees.map((assignee) => <DisplayUser user={assignee} onClick={() => deleteAssignee(assignee)} />)}
            </div>
            <h4>Not Assigned members</h4>
            {boardMembers.map((user) => <DisplayUser user={user} onClick={() => assignMember(user)} />)}
        </div>
    );
};

const EditDatePopup = ({ listId, cardId, setOpenPopup, setDueDate }) => {
    const [newDate, setNewDate] = useState(null);
    const [errors, setErrors] = useState({});

    const updateDueDate = async () => {
        const newErrors = {};

        if (!newDate) {
            newErrors.date = "Invalid date.";
            setErrors(newErrors);
            return;
        }

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const selectedDate = new Date(newDate);
        selectedDate.setHours(0, 0, 0, 0);

        if (selectedDate < today) {
            newErrors.date = "The selected date cannot be in the past.";
            setErrors(newErrors);
            return;
        }

        const formattedDate = new Date(newDate).toISOString().split("T")[0];

        try {
            const response = await queries.patch(`/api/v1/list/${listId}/card/${cardId}`, { date_end: formattedDate });
            if (response.resp === "success") {
                setDueDate(formattedDate);
                setOpenPopup(null);
            }
        } catch (error) {
            console.error("Error updating due date:", error);
        }
    };

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setTimeout(() => {
                setErrors({});
            }, 4000);
        }
    }, [errors]);

    return (
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <h4>Change due date</h4>
            <input className="date-input" type="date" onChange={(e) => setNewDate(e.target.value)} />
            {errors.date && <p className="error-message">{errors.date}</p>}
            <button className="action-button" onClick={updateDueDate}>Confirm</button>
        </div>
    );
};

const CardMainPopup = ({ card, listId, setMainCardPopup, setLists, assignees, setAssignees, labels, setLabels }) => {
    // Edition states
    const [isEditingCardName, setIsEditingCardName] = useState(false);
    const [tempName, setTempName] = useState("");
    const [isEditingCardDescription, setIsEditingCardDescription] = useState(false);
    const [tempDescription, setTempDescription] = useState("");

    const [confirmDeletePopup, setConfirmDeletePopup] = useState(false);

    // Second popup
    const [openPopup, setOpenPopup] = useState(null);

    const [dueDate, setDueDate] = useState(card.date_end ? card.date_end.split("T")[0] : null);

    const startEditingCardName = () => {
        setTempName(card.name);
        setIsEditingCardName(true);
    };

    const startEditingCardDescription = () => {
        setTempDescription(card.description);
        setIsEditingCardDescription(true);
    }

    const cancelCardDescriptionEdit = () => {
        setIsEditingCardDescription(false);
        setTempDescription("");
    }

    const handleRenameCard = async () => {
        if (!tempName.trim()) {
            return;
        }

        try {
            const response = await queries.patch(`/api/v1/list/${listId}/card/${card.id}`, { name: tempName });
            if (response.resp === "success") {
                setLists((prevLists) =>
                    prevLists.map((l) =>
                        l.id === listId
                            ? { ...l, cards: l.cards.map((c) => (c.id === card.id ? { ...c, name: tempName } : c)) }
                            : l
                    )
                );
            }
        } catch (error) {
            alert("Failed to update card title.");
        }
        setIsEditingCardName(false);
    };

    const handleEditCardDescription = async () => {
        if (!tempDescription.trim()) {
            return;
        }

        try {
            const response = await queries.patch(`/api/v1/list/${listId}/card/${card.id}`, { description: tempDescription });
            if (response.resp === "success") {
                setLists((prevLists) =>
                    prevLists.map((l) =>
                        l.id === listId
                            ? { ...l, cards: l.cards.map((c) => (c.id === card.id ? { ...c, description: tempDescription } : c)) }
                            : l
                    )
                );
            }
        } catch (error) {
            alert("Failed to update card description.");
        }
        setIsEditingCardDescription(false);
    };

    const handleDeleteCard = async () => {
        try {
            const response = await queries.delete_query(`/api/v1/list/${listId}/card/${card.id}`);

            if (response.resp === "success") {
                setLists((prevLists) =>
                    prevLists.map((l) =>
                        l.id === listId
                            ? { ...l, cards: l.cards.filter((c) => c.id !== card.id) }
                            : l
                    )
                );
            }
        } catch (error) {
            alert("Failed to delete the card.");
        }

        setConfirmDeletePopup(false);
        setMainCardPopup(false);
    };

    const handleOpenPopup = (popupType, event) => {
        const buttonRect = event.target.getBoundingClientRect();
        setOpenPopup({
            type: popupType,
            top: buttonRect.bottom + window.scrollY + 5,
            left: buttonRect.left + window.scrollX,
        });
    };

    // Fonction pour fermer le popup
    const handleClosePopup = () => {
        setOpenPopup(null);
    };

    return (
        <>
            <div className="popup-overlay">
                <div className="popup-content" style={{ width: "700px" }}>
                    <div className="popup-body">
                        {/* Contenu principal */}
                        <div className="popup-main">
                            {isEditingCardName ? (
                                <input
                                    className="card-title-input"
                                    value={tempName}
                                    onChange={(e) => setTempName(e.target.value)}
                                    onBlur={handleRenameCard}
                                    onKeyDown={(e) => e.key === "Enter" && handleRenameCard()}
                                    autoFocus
                                />
                            ) : (
                                <h3 onClick={startEditingCardName} className="card-title" style={{ cursor: "pointer" }}>
                                    {card.name}
                                </h3>
                            )}
                            {labels.length !== 0 && (
                                <div className="card-labels">
                                    {labels.map((label) => (
                                        <div key={label.id} className="card-label-container">
                                            <span className="card-label" style={{ backgroundColor: label.color, width: "30px", height: "10px" }}></span>
                                            <div className="label-popup">{label.title}</div>
                                        </div>
                                    ))}
                                </div>
                            )}
                            <div className="description-header">
                                <h4>Description</h4>
                                {isEditingCardDescription === false && <button className="edit-button" onClick={startEditingCardDescription}>Edit</button>}
                            </div>
                            {isEditingCardDescription ? (
                                <>
                                    <textarea
                                        value={tempDescription}
                                        onChange={(e) => setTempDescription(e.target.value)}
                                        autoFocus
                                    />
                                    <button onClick={handleEditCardDescription}>Confirm</button>
                                    <button onClick={cancelCardDescriptionEdit}>Cancel</button>
                                </>
                            ) : (
                                <p className="card-description">{card.description}</p>
                            )}
                            <h4>Due Date</h4>
                            {dueDate ? (
                                <p>{dueDate}</p>
                            ) : (
                                <p>No due date selected</p>
                            )}
                        </div>

                        {/* Barre d'actions à droite */}
                        <div className="popup-sidebar">
                            <h4>Actions</h4>
                            <button className="action-button" onClick={(e) => handleOpenPopup("labels", e)}>📝 Edit labels</button>
                            <button className="action-button" onClick={(e) => handleOpenPopup("assign", e)}>👤 Assign member</button>
                            <button className="action-button" onClick={(e) => handleOpenPopup("date", e)}>🕒 Edit Date</button>
                            <button className="action-button delete-card-button" onClick={() => setConfirmDeletePopup(true)}>🗑 Delete card</button>
                            <button className="action-button" onClick={() => setMainCardPopup(false)}>⬅ Back</button>
                        </div>
                    </div>
                </div>
            </div>

            {openPopup && (
                <div
                    className="popup-menu"
                    style={{ top: openPopup.top, left: openPopup.left }}
                >
                    <button className="close-popup" onClick={handleClosePopup}>✖</button>
                    <div style={{ overflow: "auto", maxWidth: "100%", width: "200px" }}>
                        {openPopup.type === "labels" &&
                            <LabelsPopup
                                cardId={card.id}
                                labels={labels}
                                setLabels={setLabels}
                            />
                        }
                        {openPopup.type === "assign" &&
                            <AssignMembersPopup
                                cardId={card.id}
                                assignees={assignees}
                                setAssignees={setAssignees}
                            />
                        }
                        {openPopup.type === "date" &&
                            <EditDatePopup
                                listId={listId}
                                cardId={card.id}
                                setOpenPopup={setOpenPopup}
                                setDueDate={setDueDate}
                            />
                        }
                    </div>
                </div>
            )}

            {/* Popup to delete the card */}
            {confirmDeletePopup && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <h3>Are you sure to delete this card?</h3>
                        <div className="popup-actions">
                            <button onClick={handleDeleteCard} className="delete-card-button">Yes</button>
                            <button onClick={() => setConfirmDeletePopup(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export const Card = ({ card, list, handleDragStart, setLists }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isMouseDown, setIsMouseDown] = useState(false);

    // Main card popup
    const [mainCardPopup, setMainCardPopup] = useState(false);

    // Additional card data
    const [assignees, setAssignees] = useState([]);
    const [labels, setLabels] = useState([]);

    const handleMouseDown = () => {
        setIsMouseDown(true);
        setIsDragging(false);
    };

    const handleMouseMove = (e) => {
        if (isMouseDown) {
            setIsDragging(true);
            e.target.draggable = true;
        }
    };

    const handleMouseUp = (e) => {
        setIsMouseDown(false);
        e.target.draggable = false;

        if (!isDragging) {
            setMainCardPopup(true);
        }
        setIsDragging(false);
    };

    useEffect(() => {
        const getAssignees = async () => {
            try {
                const getAssigneesResponse = await queries.get(`/api/v1/card/${card.id}/assignees`);

                if (getAssigneesResponse.resp === "success") {
                    const assignees = getAssigneesResponse.msg;
                    const userRequests = assignees.map(assignee =>
                        queries.get(`/api/v1/user/${assignee.user_id}`)
                    );
                    const usersResponses = await Promise.all(userRequests);
                    const validUsers = usersResponses
                        .filter(userRes => userRes.resp === "success")
                        .map(userRes => userRes.msg);
                    setAssignees(validUsers);
                }
            } catch (error) {
                console.error(error);
            }
        };
        getAssignees();
    }, [card]);

    useEffect(() => {
        const getLabels = async () => {
            try {
                const response = await queries.get(`/api/v1/card/${card.id}/labels`);
                if (response.resp === "success") {
                    setLabels(response.msg);
                }
            } catch (error) {
                console.error(error);
            }
        };
        getLabels();
    }, [card]);

    return (
        <>
            <DropIndicator beforeId={card.id} list={list} />
            <div
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
                onMouseMove={handleMouseMove}
                draggable="true"
                onDragStart={(e) => handleDragStart(e, card)}
                className="card"
            >
                {labels.length !== 0 && (
                    <div className="card-labels">
                        {labels.map((label) => (
                            <div key={label.id} className="card-label-container">
                                <span className="card-label" style={{ backgroundColor: label.color, width: "30px", height: "10px" }}></span>
                                <div className="label-popup">{label.title}</div>
                            </div>
                        ))}
                    </div>
                )}
                <p className="card-title">{card.name}</p>
                {assignees.length !== 0 && (
                    <div className="card-assignees">
                        {assignees.map((user) => (
                            <img key={user.id} src={user.favicon} alt={user.name} className="assignee-avatar" title={user.name} />
                        ))}
                    </div>
                )}
            </div>
            {mainCardPopup && (
                <CardMainPopup
                    card={card}
                    listId={list.id}
                    setMainCardPopup={setMainCardPopup}
                    setLists={setLists}
                    assignees={assignees}
                    setAssignees={setAssignees}
                    labels={labels}
                    setLabels={setLabels}
                />
            )}
        </>
    );
};
