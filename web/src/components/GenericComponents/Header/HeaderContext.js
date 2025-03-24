// Official React import
import React, { createContext, useContext, useState, useEffect } from 'react';

// Our import
import { queries } from "../../../utils/Querier";

const HeaderContext = createContext(null);

export const HeaderProvider = ({ children }) => {
    const [currentSelectedWorkspace, setCurrentSelectedWorkspace] = useState({});
    const [workspaces, setWorkspaces] = useState([]);
    const [userInfo, setUserInfo] = useState({});

    useEffect(() => {
        const getUserInfo = async () => {
            try {
                const response = await queries.get("/api/v1/user");
                if (response.resp === "success") {
                    setUserInfo(response.msg);
                }
            } catch (error) {
                console.error(error);
            }
        };
        getUserInfo();
    }, []);

    useEffect(() => {
        const getWorkspaces = async () => {
            try {
                const response = await queries.get("/api/v1/my_workspaces");
                if (response.resp === "success") {
                    setWorkspaces(response.msg);
                    const selectedWorkspace = localStorage.getItem("selectedWorkspace");
                    for (let i = 0; i < response.msg.length; i++) {
                        if (response.msg[i].name === selectedWorkspace) {
                            setCurrentSelectedWorkspace(response.msg[i]);
                            return;
                        }
                    }
                } else {
                    localStorage.removeItem("selectedWorkspace");
                    setCurrentSelectedWorkspace({});
                }
            } catch (error) {
                console.error(error);
                localStorage.removeItem("selectedWorkspace");
                setCurrentSelectedWorkspace({});
            }
        };
        getWorkspaces();
    }, []);

    return (
        <HeaderContext.Provider value={{ currentSelectedWorkspace, setCurrentSelectedWorkspace, workspaces, userInfo }}>
            {children}
        </HeaderContext.Provider>
    );
};

export const useHeader = () => useContext(HeaderContext);
