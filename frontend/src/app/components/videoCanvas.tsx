'use client';

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

import LoadingCircle from "./loadingCircle";

interface VideoCanvasProps {
    videoUrl: string;
    setLoading: (loading: boolean) => void;

}

// fix so it's the first frame

const VideoCanvas: React.FC<VideoCanvasProps> = ({ videoUrl, setLoading }: VideoCanvasProps) => {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const isDrawingRef = useRef<boolean>(false);
    const radiusRef = useRef<number>(0);
    //const [videoReady, setVideoReady] = useState<boolean>(false);
    const videoReadyRef = useRef<boolean>(false);
    let startX = 0;
    let startY = 0;

    const [circleData, setCircleData] = useState<{ x: number; y: number; radius: number } | null>(null);
    const [show, setShow] = useState(true);

    const loadingRef = useRef<boolean>(false);

    useEffect(() => {
        console.log('use effect')
        const video = videoRef.current;
        // if (video) video.currentTime = 0; video?.pause();
        const canvas = canvasRef.current;
        const ctx = canvas?.getContext('2d');

        const drawCircle = (x: number, y: number, radius: number) => {
            if (ctx && video && canvas) {
                //video.currentTime = 0;
                console.log('drawing circle');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                ctx.beginPath();
                ctx.arc(x, y, radius, 0, 2 * Math.PI);
                ctx.strokeStyle = 'red';
                ctx.stroke();
            }
        };

        video?.addEventListener('canplaythrough', () => {
            if (video.readyState >= 3 && ctx && canvas) {
                console.log('video loaded');
                video.currentTime = 0;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                video.pause();
                videoReadyRef.current = true;
                //console.log('video ready ref:', videoReadyRef.current);
            }
        });

        const handleMouseDown = (e: MouseEvent) => {
            console.log('mouse down');
            const rect = canvas?.getBoundingClientRect();
            console.log('rect mouse down', rect);

            if (!rect) return;
            console.log('rect', rect);
            startX = e.clientX - rect.left;
            startY = e.clientY - rect.top;
            isDrawingRef.current = true;

            const handleMouseMove = (e: MouseEvent) => {
                console.log('mouse move');
                if (isDrawingRef.current) {
                    console.log('drawing');
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    const r = Math.sqrt((x - startX) ** 2 + (y - startY) ** 2);
                    drawCircle(startX, startY, r);
                    radiusRef.current = r;
                }
            };

            const handleMouseUp = () => {
                if (isDrawingRef.current) {
                    const rect = canvas?.getBoundingClientRect();
                    //console.log('radius mouse up', radiusRef.current);
                    
                    if (rect) {
                        //console.log("x distance:", e.clientX - rect?.left - startX, "y distance:", e.clientY - rect?.top - startY)
                        //const r = Math.sqrt((e.clientX - rect.left - startX) ** 2 + (e.clientY - rect.top - startY) ** 2);
                        setCircleData({ x: startX, y: startY, radius: radiusRef.current });
                        //console.log("radius", r);
                        isDrawingRef.current = false;

                    }
                }
                window.removeEventListener('mousemove', handleMouseMove);
                window.removeEventListener('mouseup', handleMouseUp);
            };

            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        };

        canvas?.addEventListener('mousedown', handleMouseDown);

        return () => {
            canvas?.removeEventListener('mousedown', handleMouseDown);
        };
    }, [videoRef, canvasRef]);

    // new use effect here to send data - deal later
    useEffect(() => {
        const sendData = async () => {
            loadingRef.current = true;
            const formData = new FormData();

            if (circleData) {
                
                formData.append('cx', circleData.x.toString());
                formData.append('cy', circleData.y.toString());
                formData.append('radius', circleData.radius.toString());
                formData.append('screenWidth', window.innerWidth.toString());
                formData.append('screenHeight', window.innerHeight.toString());
            }
            setLoading(true);
            try {
                const response = await axios.post(`${apiBaseUrl}/bartracker`, formData);
                alert('Data uploaded successfully!');
                console.log('Upload response:', response.data);
            } catch (error) {
                alert('Error uploading data');
                console.error('Upload error:', error);
            } finally {
                setLoading(false);
                loadingRef.current = false;
            }

        }

        if (circleData) {
            console.log('data');
            setShow(false);
            videoReadyRef.current = false;
            sendData();
        }

    }, [circleData])

    return (

        <div className='mt-2'>
            {show &&
                <div>
                    <video className={`absolute ${videoReadyRef ? '' : 'hidden'}`} ref={videoRef} src={videoUrl} width="640" height="360" autoPlay={false} controls={false} />
                    <canvas className='absolute' ref={canvasRef} width="640" height="580" style={{ border: '1px solid red' }} />
                </div>
            }
        </div>
    );
};
// to do above: add code explaining how to draw circle
export default VideoCanvas;