// Official React import
import React, { useState } from "react";
import axios from "axios";

const ImageSearch = ({ onImageSelect }) => {
    const [query, setQuery] = useState("");
    const [images, setImages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const searchImages = async () => {
        const unsplashAccessKey = process.env.REACT_APP_UNSPLASH_ACCESS_KEY;

        setIsLoading(true);
        try {
            const response = await axios.get("https://api.unsplash.com/search/photos", {
                params: { query },
                headers: {
                    Authorization: `Client-ID ${unsplashAccessKey}`,
                },
            });
            setImages(response.data.results);
        } catch (error) {
            console.error("Error fetching images:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleClearSearch = () => {
        setQuery("");
        setImages([]);
    };

    return (
        <div>
            <div>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search for an image"
                />
                <button onClick={searchImages}>Search</button>
                <button onClick={handleClearSearch}>Clear Search</button>
            </div>
            {isLoading && <p>Loading images...</p>}
            <div className="image-grid">
                {images.map((image) => (
                    <img
                        key={image.id}
                        src={image.urls.thumb}
                        alt={image.alt_description}
                        onClick={() => onImageSelect(image.urls.full)}
                        style={{ cursor: "pointer", margin: "5px" }}
                    />
                ))}
            </div>
        </div>
    );
};

export default ImageSearch;
