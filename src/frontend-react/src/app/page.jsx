'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import DataService from "../services/DataService";
import { formatRelativeTime } from "../services/Common";

// Import the styles
import styles from "./styles.module.css";


export default function LandingPage() {
    // Component States
    const [chats, setChats] = useState([]);

    const router = useRouter();

    // Setup Component
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await DataService.GetChats(null, 20);
                setChats(response.data);
            } catch (error) {
                console.error('Error fetching chats:', error);
                setChats([]); // Set empty array in case of error
            }
        };

        fetchData();
    }, []);

    return (
        <div className={styles.container}>
            {/* Hero Section */}
            <section className={styles.hero}>
                <div className={styles.heroContent}>
                    <h1>SalesMate</h1>
                    <p>The sales training HERO you always needed</p>
                </div>
            </section>

            {/* About Section */}
            <section className={styles.about}>
                <div className={styles.aboutContent}>
                    <h2>About SalesMate</h2>
                    <p>
                        SalesMate is an innovative AI-powered platform designed to revolutionize sales training.
                        By providing secure, engaging, and scalable simulations, it empowers sales reps to master
                        their skills, close more deals, and drive business success.
                    </p>
                </div>
            </section>

            {/* Chat Grid */}
            <div className={styles.recentChats}>
                <div className={styles.recentHeader}>
                    <h2>
                        Sales Training Runs
                    </h2>
                    <button className={styles.newChatButton} onClick={() => router.push('/simulator')}>
                        <h2>Start a new run!</h2>
                    </button>
                </div>

                <div className={styles.chatGrid}>
                    {chats.map((item) => (
                        <div key={item.chat_id} className={styles.chatCard} onClick={() => router.push('/simulator?id=' + item.chat_id)}>
                            <h3 className={styles.chatTitle}>{item.title}</h3>
                            <span className={styles.chatTime}>
                                {formatRelativeTime(item.dts)}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}