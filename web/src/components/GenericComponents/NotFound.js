// Officials React import
import React from "react";
import { Link } from "react-router-dom";

const NotFound = () => {
    return (
        <div style={styles.container}>
            <h1 style={styles.title}>404</h1>
            <p style={styles.message}>Oops! The page you're looking for doesn't exist.</p>
            <Link to="/" style={styles.link}>
                Go back to the homepage
            </Link>
        </div>
    );
};

const styles = {
    container: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        backgroundColor: "#f0f4f8",
    },
    title: {
        fontSize: "6rem",
        fontWeight: "bold",
        color: "#007bff",
    },
    message: {
        fontSize: "1.5rem",
        color: "#333",
        margin: "1rem 0",
    },
    link: {
        fontSize: "1.2rem",
        color: "white",
        backgroundColor: "#007bff",
        padding: "0.8rem 1.5rem",
        textDecoration: "none",
        borderRadius: "4px",
        transition: "background-color 0.3s",
    },
};

export default NotFound;
