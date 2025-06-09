import pytest
from .data import Audio, AudioExtension, Transcription
from ..shared.supported import SubtitleExtension


class TestAudioExtension:
    
    def test_audio_extension_values(self):
        assert AudioExtension.AAC.value == "aac"
        assert AudioExtension.MP3.value == "mp3"
        assert AudioExtension.OGG.value == "ogg"
        assert AudioExtension.WAV.value == "wav"
    
    def test_audio_extension_enum_members(self):
        assert len(AudioExtension) == 4
        assert AudioExtension.AAC in AudioExtension
        assert AudioExtension.MP3 in AudioExtension
        assert AudioExtension.OGG in AudioExtension
        assert AudioExtension.WAV in AudioExtension


class TestAudio:
    
    def test_audio_creation_with_valid_data(self):
        binary_data = b"test_audio_data"
        extension = AudioExtension.MP3
        
        audio = Audio(binary=binary_data, extension=extension)
        
        assert audio.binary == binary_data
        assert audio.extension == extension
    
    def test_audio_is_frozen_dataclass(self):
        audio = Audio(binary=b"test", extension=AudioExtension.WAV)
        
        with pytest.raises(AttributeError):
            audio.binary = b"new_data"
        
        with pytest.raises(AttributeError):
            audio.extension = AudioExtension.MP3
    
    def test_audio_equality(self):
        binary_data = b"identical_data"
        extension = AudioExtension.OGG
        
        audio1 = Audio(binary=binary_data, extension=extension)
        audio2 = Audio(binary=binary_data, extension=extension)
        audio3 = Audio(binary=b"different_data", extension=extension)
        audio4 = Audio(binary=binary_data, extension=AudioExtension.MP3)
        
        assert audio1 == audio2
        assert audio1 != audio3
        assert audio1 != audio4
    
    def test_audio_with_different_extensions(self):
        binary_data = b"same_data"
        
        mp3_audio = Audio(binary=binary_data, extension=AudioExtension.MP3)
        wav_audio = Audio(binary=binary_data, extension=AudioExtension.WAV)
        ogg_audio = Audio(binary=binary_data, extension=AudioExtension.OGG)
        aac_audio = Audio(binary=binary_data, extension=AudioExtension.AAC)
        
        assert mp3_audio.extension == AudioExtension.MP3
        assert wav_audio.extension == AudioExtension.WAV
        assert ogg_audio.extension == AudioExtension.OGG
        assert aac_audio.extension == AudioExtension.AAC
    
    def test_audio_with_empty_binary(self):
        audio = Audio(binary=b"", extension=AudioExtension.MP3)
        
        assert audio.binary == b""
        assert audio.extension == AudioExtension.MP3
    
    def test_audio_with_large_binary(self):
        large_binary = b"x" * 10000
        audio = Audio(binary=large_binary, extension=AudioExtension.WAV)
        
        assert len(audio.binary) == 10000
        assert audio.extension == AudioExtension.WAV


class TestTranscription:
    
    def test_transcription_creation_with_valid_data(self):
        content = "Hello, this is a test transcription."
        extension = SubtitleExtension.SRT
        
        transcription = Transcription(content=content, extension=extension)
        
        assert transcription.content == content
        assert transcription.extension == extension
    
    def test_transcription_is_frozen_dataclass(self):
        transcription = Transcription(content="test", extension=SubtitleExtension.VTT)
        
        with pytest.raises(AttributeError):
            transcription.content = "new content"
        
        with pytest.raises(AttributeError):
            transcription.extension = SubtitleExtension.SRT
    
    def test_transcription_equality(self):
        content = "Same transcription content"
        extension = SubtitleExtension.SRT
        
        transcription1 = Transcription(content=content, extension=extension)
        transcription2 = Transcription(content=content, extension=extension)
        transcription3 = Transcription(content="Different content", extension=extension)
        transcription4 = Transcription(content=content, extension=SubtitleExtension.VTT)
        
        assert transcription1 == transcription2
        assert transcription1 != transcription3
        assert transcription1 != transcription4
    
    def test_transcription_with_different_extensions(self):
        content = "Same content"
        
        srt_transcription = Transcription(content=content, extension=SubtitleExtension.SRT)
        vtt_transcription = Transcription(content=content, extension=SubtitleExtension.VTT)
        
        assert srt_transcription.extension == SubtitleExtension.SRT
        assert vtt_transcription.extension == SubtitleExtension.VTT
    
    def test_transcription_with_empty_content(self):
        transcription = Transcription(content="", extension=SubtitleExtension.SRT)
        
        assert transcription.content == ""
        assert transcription.extension == SubtitleExtension.SRT
    
    def test_transcription_with_multiline_content(self):
        content = """Line 1
Line 2
Line 3 with special characters: @#$%^&*()"""
        transcription = Transcription(content=content, extension=SubtitleExtension.VTT)
        
        assert transcription.content == content
        assert transcription.extension == SubtitleExtension.VTT
    
    def test_transcription_with_unicode_content(self):
        content = "Hello 世界 🌍 Héllo Wörld"
        transcription = Transcription(content=content, extension=SubtitleExtension.SRT)
        
        assert transcription.content == content
        assert transcription.extension == SubtitleExtension.SRT