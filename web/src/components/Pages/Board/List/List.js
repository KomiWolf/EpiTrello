// Official React import
import React, { useState, useEffect, useRef } from "react";
import { DndContext, DragOverlay, rectIntersection } from "@dnd-kit/core";
import { SortableContext, horizontalListSortingStrategy, arrayMove } from "@dnd-kit/sortable";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

// Our import
import { Card, DropIndicator } from "./Card/Card";
import "./List.css";
import "../../../GenericComponents/Popup.css";
import { queries } from "../../../../utils/Querier";

// Component for each draggable list item
const DraggableListItem = ({ list, lists, setLists, onRename, startEditing, editingListId, tempName, setTempName, setEditingListId, setAddNewCardPopup, setSavedListId, handleDeleteClick }) => {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
        id: list.id,
        disabled: editingListId === list.id
    });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1
    };

    const getIndicators = () => {
        return Array.from(document.querySelectorAll(
            `[data-column-id="${list.id}"]`
        ));
    };

    const getNearestIndicator = (e, indicators) => {
        const DISTANCE_OFFSET = 40;
        const el = indicators.reduce(
            (closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = e.clientY - (box.top + DISTANCE_OFFSET);
                if (offset < 0 && offset > closest.offset) {
                    return { offset: offset, element: child };
                } else {
                    return closest;
                }
            },
            {
                offset: Number.NEGATIVE_INFINITY,
                element: indicators[indicators.length - 1]
            }
        );
        return el;
    };

    const clearHighlights = (els) => {
        const indicators = els || getIndicators();

        indicators.forEach((i) => {
            i.style.opacity = "0";
        });
    }

    const hightlightIndicator = (e) => {
        const indicators = getIndicators();
        clearHighlights(indicators);
        const el = getNearestIndicator(e, indicators);
        el.element.style.opacity = "1";
    };

    const handleDragCardStart = (e, card) => {
        const { list, ...cardWithoutList } = card;

        e.dataTransfer.setData("card", JSON.stringify(cardWithoutList));
    };

    const handleDragCardOver = (e) => {
        e.preventDefault();
        hightlightIndicator(e);
    };

    const handleDragCardLeave = () => {
        clearHighlights();
    }

    const handleDragCardEnd = async (e) => {
        clearHighlights();

        const droppedCard = JSON.parse(e.dataTransfer.getData("card"));
        if (!droppedCard) return;

        const targetListId = list.id;
        const indicators = getIndicators();
        const { element } = getNearestIndicator(e, indicators);
        const before = element?.dataset?.before || "-1";

        if (Number(before) === droppedCard.id) return;

        const updatedLists = lists.map((l) => ({
            ...l,
            cards: [...l.cards],
        }));

        const oldList = updatedLists.find(l => l.id === droppedCard.list_id);
        if (!oldList) return;

        const cardIndex = oldList.cards.findIndex(c => c.id === droppedCard.id);
        if (cardIndex === -1) return;

        const [cardToTransfer] = oldList.cards.splice(cardIndex, 1);
        cardToTransfer.list_id = targetListId;

        const newList = updatedLists.find(l => l.id === targetListId);
        if (!newList) return;

        if (newList.cards.some(c => c.id === droppedCard.id)) return;

        const insertAtIndex = newList.cards.findIndex(c => c.id === Number(before));

        if (insertAtIndex !== -1) {
            newList.cards.splice(insertAtIndex, 0, cardToTransfer);
        } else {
            newList.cards.push(cardToTransfer);
        }

        setLists(updatedLists);

        const position = insertAtIndex !== -1 ? insertAtIndex + 1 : newList.cards.length;

        const newCardData = {
            new_list_id: targetListId,
            position: position
        };

        try {
            await queries.patch(
                `/api/v1/list/${droppedCard.list_id}/card/${droppedCard.id}/position`,
                newCardData
            );
        } catch (error) {
            console.error('Error updating card position:', error);
        }
    };

    return (
        <div
            ref={setNodeRef}
            style={style}
            className="list"
            {...attributes}
            {...listeners}
            onKeyDown={(e) => {
                if (e.key === " " || e.key === "Enter") {
                    e.stopPropagation();
                }
            }}
        >
            <div className="list-header">
                {editingListId === list.id ? (
                    <input
                        className="list-title-input"
                        value={tempName}
                        onChange={(e) => setTempName(e.target.value)}
                        onBlur={() => setEditingListId(null)}
                        onKeyDown={(e) => e.key === "Enter" && onRename(list.id)}
                        autoFocus
                        onPointerDown={(e) => e.stopPropagation()} // Prevent drag when clicking the title
                    />
                ) : (
                    <p className="list-title">
                        {list.name}
                    </p>
                )}

                <button
                    className="edit-list-btn"
                    onClick={() => startEditing(list.id, list.name)}
                    onPointerDown={(e) => e.stopPropagation()} // Prevent drag when clicking the edit button
                >
                    ✏️
                </button>
                <button
                    className="delete-list-btn"
                    onClick={() => handleDeleteClick(list.id)}
                    onPointerDown={(e) => e.stopPropagation()} // Prevent drag when clicking the delete button
                >
                    🗑️
                </button>
            </div>
            <div
                onDragOver={handleDragCardOver}
                onDragLeave={handleDragCardLeave}
                onDrop={handleDragCardEnd}
                className="list-cards"
                onPointerDown={(e) => e.stopPropagation()}
            >
                {list.cards.map((card) => (
                    <Card key={card.id} card={card} list={list} handleDragStart={handleDragCardStart} setLists={setLists} />
                ))}
                <DropIndicator beforeId="-1" list={list} />
                <button
                    layout
                    className="add-card-btn"
                    onClick={() => {
                        setAddNewCardPopup(true);
                        setSavedListId(list.id);
                    }}
                >
                    + Add a card
                </button>
            </div>
        </div>
    );
};


const List = ({ boardId }) => {
    const [lists, setLists] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeList, setActiveList] = useState(null);
    const [editingListId, setEditingListId] = useState(null);
    const [tempName, setTempName] = useState("");
    const containerRef = useRef(null);
    const [confirmDeleteListPopup, setConfirmDeleteListPopup] = useState(false); // State to show the delete confirmation popup
    const [savedListId, setSavedListId] = useState(null); // State to store the list id to use after

    // Handle horizontal swipe (mouse drag)
    const [isMouseDown, setIsMouseDown] = useState(false);
    const [startX, setStartX] = useState(0);
    const [scrollLeft, setScrollLeft] = useState(0);

    const [addNewCardPopup, setAddNewCardPopup] = useState(false);
    const [newCardName, setNewCardName] = useState("");
    const [newCardDescription, setNewCardDescription] = useState("");

    // Set errors for input
    const [errors, setErrors] = useState({});

    // Handle delete click to show the confirmation popup
    const handleDeleteListClick = (listId) => {
        setSavedListId(listId);
        setConfirmDeleteListPopup(true);
    };

    // Handle the confirmation (delete)
    const confirmDeleteList = async () => {
        try {
            const response = await queries.delete_query(`/api/v1/list/${savedListId}`);
            if (response.resp === "success") {
                setLists(lists.filter(list => list.id !== savedListId));
            }
        } catch (error) {
            alert("Failed to delete the list.");
        }
        setConfirmDeleteListPopup(false);
    };

    // Handle cancel (close the popup without deleting)
    const cancelDeleteList = () => {
        setConfirmDeleteListPopup(false);
    };

    // Handle drag and drop
    const handleDragStart = (event) => {
        const draggedList = lists.find((list) => list.id === event.active.id);
        setActiveList(draggedList);
    };

    const handleDragEnd = async (event) => {
        const { active, over } = event;

        if (!over || active.id === over.id) {
            setActiveList(null);
            return;
        }

        const oldIndex = lists.findIndex((list) => list.id === active.id);
        const newIndex = lists.findIndex((list) => list.id === over.id);
        const updatedLists = arrayMove(lists, oldIndex, newIndex);
        setLists(updatedLists);

        try {
            await queries.patch(`/api/v1/list/${active.id}/position`, { position: newIndex + 1 });
        } catch (error) {
            console.error("Failed to update list position", error);
        }

        setActiveList(null);
    };

    const startEditing = (listId, currentName) => {
        setEditingListId(listId);
        setTempName(currentName);
    };

    const handleRename = async (listId) => {
        if (!tempName.trim()) return;

        try {
            const response = await queries.patch(`/api/v1/list/${listId}/name`, { name: tempName });
            if (response.resp === "success") {
                setLists(lists.map(list => list.id === listId ? { ...list, name: tempName } : list));
            }
        } catch (error) {
            alert("Failed to rename the list.");
        }
        setEditingListId(null);
    };

    const onMouseDown = (e) => {
        setIsMouseDown(true);
        setStartX(e.pageX - containerRef.current.offsetLeft);
        setScrollLeft(containerRef.current.scrollLeft);
    };

    const onMouseLeave = () => {
        setIsMouseDown(false);
    };

    const onMouseUp = () => {
        setIsMouseDown(false);
    };

    const onMouseMove = (e) => {
        if (!isMouseDown) return;
        const x = e.pageX - containerRef.current.offsetLeft;
        const scroll = (x - startX) * 2;
        containerRef.current.scrollLeft = scrollLeft - scroll;
    };

    const handleAddCard = async () => {
        const newErrors = {};

        if (newCardName === "") {
            newErrors.newCardName = "The name must not be empty.";
            setErrors(newErrors);
            return;
        }

        try {
            const response = await queries.post(`/api/v1/list/${savedListId}/card`, {
                name: newCardName,
                description: newCardDescription
            });
            if (response.resp === "success") {
                window.location.reload();
            }
        } catch (error) {
            alert("Failed to add card.");
        }
    };

    useEffect(() => {
        const getLists = async () => {
            try {
                const response = await queries.get(`/api/v1/board/${boardId}/lists`);
                if (response.resp === "success") {
                    const sortedLists = response.msg.sort((a, b) => a.position - b.position);

                    const listsWithCards = await Promise.all(
                        sortedLists.map(async (list) => {
                            try {
                                const cardsResponse = await queries.get(`/api/v1/list/${list.id}/cards`);
                                const sortedCards = cardsResponse.msg.sort((a, b) => a.position - b.position);
                                return {
                                    ...list,
                                    cards: sortedCards || []
                                };
                            } catch (error) {
                                return {
                                    ...list,
                                    cards: []
                                };
                            }
                        })
                    );

                    setLists(listsWithCards);
                }
            } catch (error) {
                console.error("Erreur lors de la récupération des listes:", error);
                setLists([]);
            } finally {
                setLoading(false);
            }
        };

        getLists();
    }, [boardId]);

    if (loading) return <p>Loading lists...</p>;

    return (
        <div>
            {/* Popup to add a new card */}
            {addNewCardPopup && (
                <div className="popup-overlay">
                    <div className="popup-content">
                        <h3>Add a new card</h3>
                        <label>
                            Name:
                            <input
                                type="text"
                                value={newCardName}
                                placeholder="Enter a name"
                                onChange={(e) => setNewCardName(e.target.value)}
                            />
                            {errors.newCardName && <p className="error-message">{errors.newCardName}</p>}
                        </label>
                        <label>
                            Description:
                            <textarea
                                value={newCardDescription}
                                placeholder="Enter a description"
                                onChange={(e) => setNewCardDescription(e.target.value)}
                                onInput={(e) => {
                                    e.target.style.height = "auto";
                                    e.target.style.height = `${e.target.scrollHeight}px`;
                                }}
                            />
                        </label>
                        <div className="popup-actions">
                            <button onClick={handleAddCard}>Create</button>
                            <button onClick={() => setAddNewCardPopup(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Popup to delete a list */}
            {
                confirmDeleteListPopup && (
                    <div className="popup-overlay">
                        <div className="popup-content">
                            <h3>Are you sure to delete this list?</h3>
                            <div className="popup-actions">
                                <button onClick={confirmDeleteList}>Yes</button>
                                <button onClick={cancelDeleteList}>Cancel</button>
                            </div>
                        </div>
                    </div>
                )
            }
            <DndContext
                collisionDetection={rectIntersection}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
            >
                <SortableContext items={lists.map(list => list.id)} strategy={horizontalListSortingStrategy}>
                    <div
                        ref={containerRef}
                        className="list-container"
                        onMouseDown={onMouseDown}
                        onMouseLeave={onMouseLeave}
                        onMouseUp={onMouseUp}
                        onMouseMove={onMouseMove}
                        style={{ cursor: isMouseDown ? "grabbing" : "grab" }}
                    >
                        {lists.map((list) => (
                            <DraggableListItem
                                key={list.id}
                                list={list}
                                lists={lists}
                                setLists={setLists}
                                onRename={handleRename}
                                startEditing={startEditing}
                                editingListId={editingListId}
                                tempName={tempName}
                                setTempName={setTempName}
                                setEditingListId={setEditingListId}
                                setAddNewCardPopup={setAddNewCardPopup}
                                setSavedListId={setSavedListId}
                                handleDeleteClick={handleDeleteListClick}
                            />
                        ))}
                    </div>
                </SortableContext>

                <DragOverlay>
                    {activeList && (
                        <DraggableListItem
                            list={activeList}
                            lists={lists}
                            setLists={setLists}
                            onRename={handleRename}
                            startEditing={startEditing}
                            editingListId={editingListId}
                            tempName={tempName}
                            setTempName={setTempName}
                            setEditingListId={setEditingListId}
                            setAddNewCardPopup={setAddNewCardPopup}
                            setSavedListId={setSavedListId}
                            handleDeleteClick={handleDeleteListClick}
                        />
                    )}
                </DragOverlay>
            </DndContext>
        </div>
    );
};

export default List;
