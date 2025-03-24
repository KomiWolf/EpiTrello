// Officials React import
import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';

// Our import
import "../Popup.css";
import ImageSearch from "../ImageSearch/ImageSearch";
import { queries } from "../../../utils/Querier";

const CreateWorkspacePopup = ({ setIsPopupOpen }) => {
    const navigate = useNavigate();
    const [workspaceName, setWorkspaceName] = useState("");
    const [description, setDescription] = useState("");
    const [favicon, setFavicon] = useState(null);
    const [previewFavicon, setPreviewFavicon] = useState(null);
    const [uploadOption, setUploadOption] = useState(""); // "local" or "unsplash"
    const [faviconSource, setFaviconSource] = useState(""); // "local" ou "unsplash"

    // Set errors for input
    const [errors, setErrors] = useState({});

    const handleLocalFaviconChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setFavicon(file);
            const reader = new FileReader();
            reader.onload = () => setPreviewFavicon(reader.result);
            reader.readAsDataURL(file);
        }
        setFaviconSource("local");
        setUploadOption("");
    };

    const handleUnsplashFaviconChange = (imageUrl) => {
        setFavicon(imageUrl);
        setPreviewFavicon(imageUrl);
        setFaviconSource("unsplash");
        setUploadOption("");
    }

    const handleCreate = async () => {
        const newErrors = {};

        if (!workspaceName || workspaceName.length === 0) {
            newErrors.workspaceName = "The workspace name must not be empty.";
            setErrors(newErrors);
            return;
        }

        if (!favicon || favicon.length === 0) {
            newErrors.favicon = "You must choose an icon for your workspace.";
            setErrors(newErrors);
            return;
        }
        const formData = new FormData();

        formData.append("name", workspaceName);
        formData.append("description", description);
        if (faviconSource === "local" && favicon) {
            formData.append("favicon", favicon);
        } else if (faviconSource === "unsplash" && favicon) {
            const urlResponse = await fetch(favicon);
            const blob = await urlResponse.blob();
            formData.append("favicon", blob, `unsplash_${Date.now()}.jpg`);
        }

        try {
            const response = await queries.post("/api/v1/workspace", formData);

            if (response.resp === "success") {
                localStorage.setItem("selectedWorkspace", workspaceName);
                navigate("/menu");
                window.location.reload();
            }
        } catch (error) {
            alert("The workspace was not created successfully.");
            console.error(error);
        }
        setIsPopupOpen(false);
    };

    useEffect(() => {
        if (Object.keys(errors).length > 0) {
            setTimeout(() => {
                setErrors({});
            }, 4000);
        }
    }, [errors]);

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <h3>Create a New Workspace</h3>
                <div>
                    <label>Workspace Name</label>
                    <input
                        type="text"
                        placeholder="Enter the workspace name"
                        value={workspaceName}
                        onChange={(e) => setWorkspaceName(e.target.value)}
                    />
                    {errors.workspaceName && <p className="error-message">{errors.workspaceName}</p>}
                </div>
                <div>
                    <label>Description (optional)</label>
                    <textarea
                        placeholder="Enter the workspace description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                    ></textarea>
                </div>
                <div>
                    <label>Icon</label>
                    <button onClick={() => setUploadOption("local")}>Upload Local</button>
                    <button onClick={() => setUploadOption("unsplash")}>Search Unsplash</button>

                    {/* Local file upload */}
                    {uploadOption === "local" && (
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleLocalFaviconChange}
                        />
                    )}

                    {/* Unsplash image search */}
                    {uploadOption === "unsplash" && (
                        <ImageSearch onImageSelect={handleUnsplashFaviconChange} />
                    )}
                    {previewFavicon && (
                        <div className="favicon-preview">
                            <img src={previewFavicon} alt="Favicon Preview" />
                        </div>
                    )}
                    {errors.favicon && <p className="error-message">{errors.favicon}</p>}
                </div>
                <div className="popup-actions">
                    <button onClick={handleCreate}>Create</button>
                    <button onClick={() => setIsPopupOpen(false)}>Cancel</button>
                </div>
            </div>
        </div>
    );
};

export default CreateWorkspacePopup;
