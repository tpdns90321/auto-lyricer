import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import toWebVTT from "srt-webvtt";
import videojs from "video.js";
import "videojs-youtube";
import "video.js/dist/video-js.css";

import { pb } from "./pb";

const initVideo = async (setVideo: Dispatch<SetStateAction<string>>, videoID: string | undefined) => {
  if (!videoID) return;
  const targetVideoList = await pb.collection("videos").getList(1, 1, { filter: `videoID = "${videoID}"` });
  if (targetVideoList.totalItems === 0) {
    const video = await pb.collection("videos").create({ videoID: videoID });
    setVideo(video.id);
  }
  setVideo(targetVideoList.items[0].id)
}

type TranscriptionData = {
  id: string;
  video: string;
  transcription?: string;
};

const createTranscription = async (setTranscription: Dispatch<SetStateAction<string>>, video: string) => {
  const transcription = await pb.collection('transcriptions').create({ video });
  setTranscription(transcription.id);
}

type LyricsData = {
  id: string;
  referenced?: string;
  language?: string;
  transcription?: string;
  plain?: string;
  srt?: string;
};

const Video = () => {
  const { id: youtubeVideoID } = useParams();
  const [video, setVideo] = useState<string>('');
  const [transcription, setTranscription] = useState<string>('');
  const [transcriptionData, setTranscriptionData] = useState<TranscriptionData | null>(null);
  const [original, setOriginal] = useState<string>('');
  const [lyricData, setLyricData] = useState<LyricsData | null>(null);
  const [translationData, setTranslationData] = useState<LyricsData | null>(null);
  const [webVTT, setWebVTT] = useState<string>('');
  const videoRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<ReturnType<typeof videojs> | null>(null);

  useEffect(() => {
    initVideo(setVideo, youtubeVideoID);
  }, [youtubeVideoID]);

  useEffect(() => {
    if (video) {
      createTranscription(setTranscription, video);
    }
  }, [video]);

  useEffect(() => {
    if (transcription) {
      const initTranscription = async () => {
        pb.collection('transcriptions').subscribe<TranscriptionData>(transcription, (data) => {
          setTranscriptionData(data.record);
        });
      }
      initTranscription()
    }
  }, [transcription]);

  const handleOriginalChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setOriginal(e.target.value);
  }

  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const handleStartSync = async () => {
    if (isSyncing) return;
    setIsSyncing(true);
    const lyric = await pb.collection('lyrics').create<LyricsData>({ transcription: transcriptionData?.id, plain: original });
    pb.collection('lyrics').subscribe<LyricsData>(lyric.id, (data) => {
      setLyricData(data.record);
    });
  };

  const [isTranslating, setIsTranslating] = useState<boolean>(false);
  const handleStartTranslate = async () => {
    if (isTranslating) return;
    setIsTranslating(true);
    const translation = await pb.collection('lyrics').create<LyricsData>({ referenced: lyricData?.id, language: 'ko' });
    pb.collection('lyrics').subscribe<LyricsData>(translation.id, (data) => {
      setTranslationData(data.record);
    });
  }

  useEffect(() => {
    if (translationData?.srt) {
      toWebVTT(new Blob([translationData.srt], { type: 'plain/text' })).then((webvtt) => {
        setWebVTT(webvtt);
      });
    }
  }, [translationData]);

  useEffect(() => {
    const videoElement = document.createElement('video-js'); 
    videoRef?.current?.appendChild(videoElement);

    playerRef.current = videojs(videoElement, {
      controls: true,
      responsive: true,
      width: '720',
      height: '480',
      sources: [{
        src: 'https://www.youtube.com/watch?v=' + youtubeVideoID,
        type: 'video/youtube',
      }],
    });

    return () => {
      playerRef.current?.dispose();
    }
  }, [youtubeVideoID]);

  useEffect(() => {
    if (playerRef.current && webVTT) {
      playerRef.current.addRemoteTextTrack({
        kind: 'captions',
        src: webVTT,
        srcLang: 'ko',
        label: 'Korean',
        default: true,
        selected: true,
      });
    }
    return () => {
      playerRef.current?.removeRemoteTextTrack();
    }
  }, [webVTT]);

  return (
    <div className="flex flex-1 items-center justify-center h-full flex-col">
      <div ref={videoRef} data-vjs-player />
      <div className="mt-5 flex flex-col items-center bg-gray-100 rounded-lg p-2 shadow-sm">
        <div className="flex items-center">
          <textarea
            className="bg-transparent outline-none text-gray-700 placeholder-gray-400 px-2 min-h-16"
            contentEditable={false}
            disabled={true}
            value={transcriptionData?.transcription}
          />
          { transcriptionData?.transcription ? (
            <textarea
              className="flex-grow bg-transparent outline-none text-gray-700 placeholder-gray-400 px-2 min-h-16"
              placeholder="Put Original Lyrics"
              id="original"
              onChange={handleOriginalChange}
              disabled={isSyncing}
            />
          ) : null }
          { lyricData?.srt ? (
            <textarea
              className="bg-transparent outline-none text-gray-700 placeholder-gray-400 px-2 min-h-16"
              contentEditable={false}
              value={lyricData.srt}
              disabled={true}
            />
          ) : null }
          { translationData?.srt ? (
            <textarea
              className="bg-transparent outline-none text-gray-700 placeholder-gray-400 px-2 min-h-16"
              contentEditable={false}
              value={translationData.srt}
              disabled={true}
            />
          ) : null }
        </div>
        { transcriptionData?.transcription ? (
          <button
            className="mt-2 bg-blue-500 text-white rounded-lg p-2"
            disabled={isSyncing}
            onClick={handleStartSync}
          >{!isSyncing ? '싱크 맞추기' : '동기화 ' + (lyricData?.srt ? '완료' : '중') }</button>
        ) : null }
        { lyricData?.srt ? (
          <button
            className="mt-2 bg-blue-500 text-white rounded-lg p-2"
            disabled={isTranslating}
            onClick={handleStartTranslate}
          >{'번역' + (isTranslating ? '중' : '하기')}</button>
        ) : null }
      </div>
    </div>
  );
};

export default Video;
