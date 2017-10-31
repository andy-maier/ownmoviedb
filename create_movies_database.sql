-- phpMyAdmin SQL Dump
-- version 4.6.6
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Oct 31, 2017 at 02:59 PM
-- Server version: 5.5.57-MariaDB
-- PHP Version: 5.6.31

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `movies`
--
CREATE DATABASE IF NOT EXISTS `movies` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `movies`;

-- --------------------------------------------------------

--
-- Table structure for table `Cabinet`
--

CREATE TABLE `Cabinet` (
  `idCabinet` int(10) UNSIGNED NOT NULL COMMENT 'Single primary key of the table.',
  `idCabinetType` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT 'Foreign key for the type of media cabinet.',
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the media cabinet, for human consumption. Should be unique.\nExamples:\n- DS12 File Server\n- Living Room Cabinet Left Side',
  `SMBServerHost` text COLLATE utf8_unicode_ci COMMENT 'If the media cabinet is an SMB/CIFS file server: The IP address or DNS host name of the file server.\nOtherwise: <null>.',
  `SMBServerShare` text COLLATE utf8_unicode_ci COMMENT 'If the media cabinet is an SMB/CIFS file server: The share name of the shared resource on the file server.\nOtherwise: <null>.',
  `PhysicalLocation` text COLLATE utf8_unicode_ci COMMENT 'If the media cabinet is a physical cabinet: Description of the physical location, for human consumption.\nOtherwise: <null>.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A cabinet that can contain movie media.';

-- --------------------------------------------------------

--
-- Table structure for table `FixedAudioBitrateMode`
--

CREATE TABLE `FixedAudioBitrateMode` (
  `idAudioBitrateMode` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Convenience name of the audio bitrate mode.',
  `FieldValue` text COLLATE utf8_unicode_ci COMMENT 'Value of the field in the medium (as reported by MediaInfo).',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the audio bitrate mode.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='An audio bitrate mode.\nFor example: Constant, Variable.';

--
-- Dumping data for table `FixedAudioBitrateMode`
--

INSERT INTO `FixedAudioBitrateMode` (`idAudioBitrateMode`, `Name`, `FieldValue`, `Description`) VALUES
('VARIABLE', 'Variable', 'Variable', 'Variable audio bitrate'),
('CONSTANT', 'Constant', 'Constant', 'Constant bit rate');

-- --------------------------------------------------------

--
-- Table structure for table `FixedAudioChannelType`
--

CREATE TABLE `FixedAudioChannelType` (
  `idAudioChannelType` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Convenience name of the audio channel type.',
  `FieldValue` text COLLATE utf8_unicode_ci COMMENT 'Value of the field in the medium (as reported by MediaInfo).',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the audio channel type.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='An audio channel type of a medium.\nFor example: mono, joint ';

--
-- Dumping data for table `FixedAudioChannelType`
--

INSERT INTO `FixedAudioChannelType` (`idAudioChannelType`, `Name`, `FieldValue`, `Description`) VALUES
('MONO', 'Mono', 'Mono', 'One channel, in mono'),
('JSTEREO', 'Joint Stereo', 'JStereo', 'Two channels, in joint stereo'),
('LRSTEREO', 'Left-Right Stereo', 'LRStereo', 'Two channels, in left-right stereo');

-- --------------------------------------------------------

--
-- Table structure for table `FixedAudioFormat`
--

CREATE TABLE `FixedAudioFormat` (
  `idAudioFormat` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Convenience name of the audio format.\nFor example: MP3.',
  `LongName` text COLLATE utf8_unicode_ci COMMENT 'Official long name of the audio format.\nFor example: MPEG-2 layer 3.',
  `FormatFieldValue` text COLLATE utf8_unicode_ci COMMENT 'Value of the format field in the medium (as reported by MediaInfo).',
  `ProfileFieldValue` text COLLATE utf8_unicode_ci COMMENT 'Value of the format profile field in the medium (as reported by MediaInfo).\nNULL if that field does not matter for this format.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='An audio format.\nFor example: AAC, MP3.';

--
-- Dumping data for table `FixedAudioFormat`
--

INSERT INTO `FixedAudioFormat` (`idAudioFormat`, `Name`, `LongName`, `FormatFieldValue`, `ProfileFieldValue`) VALUES
('AAC', 'AAC', 'Advanced Audio Coding', 'AAC', NULL),
('MP3', 'MP3', 'MPEG-2 Audio Layer III', 'MPEG Audio', NULL),
('AC-3', 'AC-3', 'Audio Codec 3', 'AC-3', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `FixedCabinetType`
--

CREATE TABLE `FixedCabinetType` (
  `idCabinetType` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the cabinet type.',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the cabinet type.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A type of media cabinet.\nFor example: SMB server, physical c';

--
-- Dumping data for table `FixedCabinetType`
--

INSERT INTO `FixedCabinetType` (`idCabinetType`, `Name`, `Description`) VALUES
('SMB', 'SMB Server', 'SMB Server'),
('PHYSICAL', 'Physikalischer Platz', 'Physikalischer Platz (zB. Schrank)');

-- --------------------------------------------------------

--
-- Table structure for table `FixedContainerFormat`
--

CREATE TABLE `FixedContainerFormat` (
  `idContainerFormat` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Short name of the container format.\nFor example, MP4',
  `LongName` text COLLATE utf8_unicode_ci COMMENT 'Long name of the container format.\nFor example, MPEG-4.',
  `FileExtension` text COLLATE utf8_unicode_ci COMMENT 'File extension of the container format, in lower case and without leading dot.\nFor example: mp4.',
  `FieldValue` text COLLATE utf8_unicode_ci COMMENT 'Value of the format field in the medium (as reported by MediaInfo).'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A container format for the medium.\nFor example: DVD, BD, MP4';

--
-- Dumping data for table `FixedContainerFormat`
--

INSERT INTO `FixedContainerFormat` (`idContainerFormat`, `Name`, `LongName`, `FileExtension`, `FieldValue`) VALUES
('MP4', 'MP4', 'MPEG-4 Part 14', 'mp4', 'MPEG-4'),
('AVI', 'AVI', 'Audio Video Interleave', 'avi', 'AVI');

-- --------------------------------------------------------

--
-- Table structure for table `FixedGenreType`
--

CREATE TABLE `FixedGenreType` (
  `idGenreType` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the genre type.',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the genre type.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A genre type.\nFor example: Gattung, Genre, Zielgruppe';

--
-- Dumping data for table `FixedGenreType`
--

INSERT INTO `FixedGenreType` (`idGenreType`, `Name`, `Description`) VALUES
('Gattung', 'Gattung', 'Eine Klassifizierung der \"Großgattungen\" des Films, zB. Spielfilm oder Dokumentarfilm.'),
('Genre', 'Genre', 'Eine Gruppe von Filmen, die unter einem spezifischen Aspekt Gemeinsamkeiten aufweisen.'),
('Stilrichtung', 'Stilrichtung', 'Vorhandensein bestimmter Stilrichtungen, zB. Film noir.'),
('Stilmittel', 'Stilmittel', 'Ein stilistisches oder technisches Mittel im Film.'),
('VeroeffentlichungsArt', 'Veröffentlichungs-Art', 'Klassifizierung eines Films über die Art seiner Veröffentlichung, zB. Kinofilm.'),
('ProduktionsArt', 'Produktions-Art', 'Klassifizierung eines Films über die Art seiner Produktionsbedingungen, zB. Autorenfilm.'),
('Laenge', 'Länge', 'Klassifizierung eines Films über seine Länge, zB. Kurzfilm.'),
('WeltArt', 'Welt-Art', 'Klassifizierung eines Films darüber ob er eine reale Welt oder eine Trickwelt darstellt.'),
('Zielgruppe', 'Zielgruppe', 'Klassifizierung eines Films über seine Zielgruppe (zB. Kinderfilm).');

-- --------------------------------------------------------

--
-- Table structure for table `FixedMediumType`
--

CREATE TABLE `FixedMediumType` (
  `idMediumType` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the medium type.',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the medium type.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A type of medium.\nFor example: DVD, BD, file.';

--
-- Dumping data for table `FixedMediumType`
--

INSERT INTO `FixedMediumType` (`idMediumType`, `Name`, `Description`) VALUES
('DVD', 'DVD', 'DVD'),
('BD', 'BD', 'Blueray Disc'),
('FILE', 'File', 'File');

-- --------------------------------------------------------

--
-- Table structure for table `FixedPersonRoleType`
--

CREATE TABLE `FixedPersonRoleType` (
  `idPersonRoleType` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the person role type.',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the person role type.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A type of role for a person in a movie.\nFor example: directo';

--
-- Dumping data for table `FixedPersonRoleType`
--

INSERT INTO `FixedPersonRoleType` (`idPersonRoleType`, `Name`, `Description`) VALUES
('DIRECTOR', 'Regisseur', 'Regisseur'),
('ACTOR', 'Schauspieler', 'Schauspieler'),
('MUSIC', 'Musik', 'Musik (Leitung)'),
('AUTHOR', 'Drehbuch', 'Drehbuchautor');

-- --------------------------------------------------------

--
-- Table structure for table `FixedQuality`
--

CREATE TABLE `FixedQuality` (
  `idVideoQuality` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the video quality.',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the video quality.',
  `Index` int(11) DEFAULT NULL COMMENT 'The relative index for the video quality (the higher, the better).',
  `MinimumBitrateNormal` float DEFAULT NULL COMMENT 'The minimum video bitrate (in kbit/s) for a normal movie (other than black&white or animated) to have this video quality.',
  `MinimumBitrateBW` float DEFAULT NULL COMMENT 'The minimum video bitrate (in kbit/s) for a black&white movie to have this video quality.',
  `MinimumBitrateAnimated` float DEFAULT NULL COMMENT 'The minimum video bitrate (in kbit/s) for a animated movie to have this video quality.',
  `MinimumSamplingWidth` int(11) DEFAULT NULL COMMENT 'The minimum video sampling width (in pixel) for a movie to have this video quality.',
  `MinimumSamplingHeight` int(11) DEFAULT NULL COMMENT 'The minimum video sampling height (in pixel) for a movie to have this video quality.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A video quality for the movie medium.\nFor example: HD, SD.';

--
-- Dumping data for table `FixedQuality`
--

INSERT INTO `FixedQuality` (`idVideoQuality`, `Name`, `Description`, `Index`, `MinimumBitrateNormal`, `MinimumBitrateBW`, `MinimumBitrateAnimated`, `MinimumSamplingWidth`, `MinimumSamplingHeight`) VALUES
('FHD', 'FHD', 'Auflösung mindestens 1920x1080, Video-Bitrate mindestens 4000 kbit/s (SW: 3200, Trick: 2400)', 12, 4000, 3200, 2400, 1920, 1080),
('HD', 'HD', 'Auflösung mindestens 1280x720, Video-Bitrate mindestens 2000 kbit/s (SW: 1600, Trick: 1200)', 10, 2000, 1600, 1200, 1280, 720),
('HQ', 'HQ', 'Auflösung mindestens 700x550, Video-Bitrate mindestens 1000 kbit/s (SW: 800, Trick: 600)', 6, 1000, 800, 600, 700, 550),
('SD', 'SD', 'Auflösung weniger als 700x550, Video-Bitrate mindestens 500 kbit/s (SW: 400, Trick: 300)', 2, 500, 400, 300, 0, 0),
('HD+HQ', 'HD+HQ', 'Größtenteils HD, einige Teile in HQ das auf HD hochskaliert wurde', 8, 2000, 1600, 1200, 1280, 720),
('HD+SD', 'HD+SD', 'Größtenteils HD, einige Teile in SD (und evt. HQ) das auf HD hochskaliert wurde', 8, 2000, 1600, 1200, 1280, 720),
('HQ+SD', 'HQ+SD', 'Größtenteils HQ, einige Teile in SD das auf HQ hochskaliert wurde', 4, 1000, 800, 600, 700, 550),
('FHD-low', 'FHD-low', 'Auflösung wie bei FHD, aber die Video-Bitrate wird nicht erreicht', 11, 0, 0, 0, 1920, 1080),
('HD-low', 'HD-low', 'Auflösung wie bei HD, aber die Video-Bitrate wird nicht erreicht', 9, 0, 0, 0, 1280, 720),
('HQ-low', 'HQ-low', 'Auflösung wie bei HQ, aber die Video-Bitrate wird nicht erreicht', 5, 0, 0, 0, 700, 550),
('SD-low', 'SD-low', 'Auflösung wie bei SD, aber die Video-Bitrate wird nicht erreicht', 1, 0, 0, 0, 0, 0),
('HD+HQ-low', 'HD+HQ-low', 'Auflösung wie bei HD+HQ, aber die Video-Bitrate wird nicht erreicht', 7, 0, 0, 0, 1280, 720),
('HD+SD-low', 'HD+SD-low', 'Auflösung wie bei HD+SD, aber die Video-Bitrate wird nicht erreicht', 7, 0, 0, 0, 1280, 720),
('HQ+SD-low', 'HQ+SD-low', 'Auflösung wie bei HQ+SD, aber die Video-Bitrate wird nicht erreicht', 3, 0, 0, 0, 700, 550),
('SD-HQ', 'SD-HQ', 'SD auf HQ hochskaliert', 4, 0, 0, 0, 0, 0),
('SD-HD', 'SD-HD', 'SD auf HD hochskaliert', 8, 0, 0, 0, 0, 0),
('HQ-HD', 'HQ-HD', 'HQ auf HD hochskaliert', 8, 0, 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `FixedStatus`
--

CREATE TABLE `FixedStatus` (
  `idStatus` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the status.',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the status.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A status of a movie media.\nFor example: shared, in work';

--
-- Dumping data for table `FixedStatus`
--

INSERT INTO `FixedStatus` (`idStatus`, `Name`, `Description`) VALUES
('SHARED', 'Auf Medienserver', 'Auf dem Medienserver bereitgestellt'),
('DISABLED', 'Auf Medienserver (Disabled)', 'Auf dem Medienserver bereitstellbar, aber derzeit nicht bereitgestellt'),
('WORK', 'In Bearbeitung', 'Die Filmdatei ist in Bearbeitung (zB. wartet auf Bearbeitung oder auf das Prozessieren des Bearbeitungsauftrags)'),
('DUPLICATE', 'Duplikat', 'Die Filmdatei ist ein Duplikat einer anderen vorhandenen Filmdatei.'),
('MISSINGPARTS', 'Wartet auf fehlende Teile', 'Es fehlen Teile des Films, zB. Anfang oder Ende'),
('INVALIDFN', 'Ungültiger Filename', 'Ungültiges Format des Filenamens');

-- --------------------------------------------------------

--
-- Table structure for table `FixedVideoFormat`
--

CREATE TABLE `FixedVideoFormat` (
  `idVideoFormat` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Convenience name of the video format.\nFor example: AVC.',
  `LongName` text COLLATE utf8_unicode_ci COMMENT 'Official long name of the video format.\nFor example: Advanced Video Coding.',
  `FormatFieldValue` text COLLATE utf8_unicode_ci COMMENT 'Value of the format field in the medium (as reported by MediaInfo).',
  `ProfileFieldValue` text COLLATE utf8_unicode_ci COMMENT 'Value of the format profile field in the medium (as reported by MediaInfo).\nNULL if that field does not matter for this format.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A video format.\nFor example: AVC, DivX.';

--
-- Dumping data for table `FixedVideoFormat`
--

INSERT INTO `FixedVideoFormat` (`idVideoFormat`, `Name`, `LongName`, `FormatFieldValue`, `ProfileFieldValue`) VALUES
('AVC', 'AVC', 'Advanced Video Coding', 'AVC', NULL),
('DIVX', 'DivX', 'DivX (MPEG-4 Visual)', 'MPEG-4 Visual', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `FixedVideoFramerateMode`
--

CREATE TABLE `FixedVideoFramerateMode` (
  `idVideoFramerateMode` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Convenience name of the video framerate mode.',
  `FieldValue` text COLLATE utf8_unicode_ci COMMENT 'Value of the field in the medium (as reported by MediaInfo).',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Description of the video framerate mode.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A video frame rate mode.\nFor example: Constant, Variable.';

--
-- Dumping data for table `FixedVideoFramerateMode`
--

INSERT INTO `FixedVideoFramerateMode` (`idVideoFramerateMode`, `Name`, `FieldValue`, `Description`) VALUES
('VARIABLE', 'Variable', 'Variable', 'Variable frame rate'),
('CONSTANT', 'Constant', 'Constant', 'Constant frame rate');

-- --------------------------------------------------------

--
-- Table structure for table `Genre`
--

CREATE TABLE `Genre` (
  `idGenre` int(10) UNSIGNED NOT NULL,
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the genre, in mixed case.',
  `idGenreType` varchar(30) COLLATE utf8_unicode_ci NOT NULL COMMENT 'Type of the genre.',
  `idParentGenre` int(10) UNSIGNED DEFAULT NULL COMMENT 'Foreign key to the parent gerne of this genre.\nNULL, if this genre does not have a parent genre, or if a parent genre is not applicable.',
  `idSynonymOfGenre` int(10) UNSIGNED DEFAULT NULL COMMENT 'Foreign key to the genre this genre is a synonym of.\nNULL, if this genre is not a synonym of another genre.',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Brief description of the genre that allows determining when to apply it to a movie.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A movie genre.';

--
-- Dumping data for table `Genre`
--

INSERT INTO `Genre` (`idGenre`, `Name`, `idGenreType`, `idParentGenre`, `idSynonymOfGenre`, `Description`) VALUES
(1, 'Kinofilm', 'VeroeffentlichungsArt', NULL, NULL, 'Ein Begriff für Filme, die für die Vorführung im Kino produziert werden.'),
(2, 'Fernsehfilm', 'VeroeffentlichungsArt', NULL, NULL, 'Ein Begriff für Filme, die für die Fernsehausstrahlung produziert werden. Die Produktionen werden in der Regel von einer oder mehreren Rundfunkgesellschaften in Auftrag gegeben und ganz oder teilweise finanziert.'),
(3, 'Mediafilm', 'VeroeffentlichungsArt', NULL, NULL, 'Ein Begriff für Filme, die für die Veröffentlichung auf einem Medium (zB. BD, DVD, VHS, Internet) produziert werden.'),
(4, 'Autorenfilm', 'ProduktionsArt', NULL, NULL, 'Ein Begriff für Filme, in denen der Regisseur sämtliche künstlerischen Aspekte des Films wie Drehbuch oder Schnitt wesentlich mitbestimmt und in denen er, vergleichbar einem Romanautor oder einem bildenden Künstler, als (alleiniger) Autor des Werks angesehen werden kann oder soll. Der Begriff Autorenfilm selbst, sowie seine genaue Definition und Abgrenzung, sind in der Filmwissenschaft jedoch umstritten.'),
(5, 'Independentfilm', 'ProduktionsArt', NULL, NULL, 'Ursprünglich ein Begriff für Filme, die außerhalb (also ohne Finanzierung oder Vertriebsunterstützung) des US-amerikanischen Studiosystems produziert wurden. Der Independentfilm war also zunächst ein rein amerikanisches Phänomen, das mittlerweile aber auch in anderen Ländern Verbreitung gefunden hat.  Er entstand aus einer Unzufriedenheit einiger Filmemacher, die sich von den großen Studios zu sehr gegängelt fühlten und die ihre künstlerischen Ideen verwirklicht sehen wollten. Sie machten sich auf die Suche nach anderen Finanzierern und anderen Distributionswegen, um ihre Filme produzieren zu können. Independentfilme sind zumeist „kleine“ Filme: Sie sind mit geringem Geldeinsatz und unter hohem Zeitdruck hergestellt, dafür gehen sie kreativ mit ihren Geschichten um und erzählen, ohne den Hollywood-Erzählmustern zu folgen.'),
(6, 'Indie-Film', 'ProduktionsArt', NULL, 5, 'Alternativer Begriff für Independentfilm.'),
(7, 'Monumentalfilm', 'ProduktionsArt', NULL, NULL, 'Ein Begriff für Filme in denen mehrere formale, aber auch inhaltliche Kriterien zusammen erfüllt werden, die einen Film zu einem monumentalen Werk (im Sinn von „überdimensional“ und „herausragend“) machen. Zu den formalen Kriterien eines Monumentalfilms gehören beispielsweise neben hohen Produktionskosten eine aufwendige Inszenierung, in der Massenszenen mit einer ungewöhnlich hohen Anzahl an Statisten, Kostümen und/oder gesondert hergestellten bzw. nachgebauten Kulissen eine wichtige Bedeutung einnehmen.'),
(8, 'Kurzfilm', 'Dauer', NULL, NULL, 'Ein Begriff für Filme mit einer Länge von in der Regel weniger als 30 Minuten. Allerdings sind die Grenzen hier nicht klar definiert; so gelten bei Kurzfilmfestivals oftmals unterschiedliche Längenbegrenzungen.'),
(9, 'Mittellangfilm', 'Dauer', NULL, NULL, 'Ein Begriff für Filme mit einer Länge zwischen der eines Kurzfilms und der eines Langfilms. Die Bezeichnung Mittellangfilm ist im deutschen Sprachraum kaum verbreitet, sie ist vor allem ein Phänomen in Ländern mit romanischen Sprachen.'),
(10, 'Langfilm', 'Dauer', NULL, NULL, 'Ein Begriff für Filme mit einer Länge von ? (jedenfalls lang :-)'),
(11, 'Realfilm', 'WeltArt', NULL, NULL, 'Ein Begriff für Filme, die in denen Vorgänge, Ereignisse und Handlungen in einer real dargestellten Welt von real dargestellten Akteuren inszeniert werden. Das Gegenstück zum Realfilm ist der Trickfilm.'),
(12, 'Trickfilm', 'WeltArt', NULL, NULL, 'Ein Begriff für Filme in denen Vorgänge, Ereignisse und Handlungen in einer künstlich dargestellten Welt von künstlich dargestellten Akteuren inszeniert werden. Spezielle Kategorien von Trickfilmen sind Computeranimationsfilme, Zeichentrickfilme, Puppentrickfilme, Knetanimationsfilme. Das Gegenstück zum Trickfilm ist der Realfilm.'),
(13, 'Animationsfilm', 'WeltArt', NULL, 12, 'Alternativer Begriff für Trickfilm.'),
(14, 'Kinderfilm', 'Zielgruppe', NULL, NULL, 'Ein Begriff für Filme, die sich in erster Linie an Kinder richten. In thematischer und stilistischer Hinsicht gibt es kaum Beschränkungen, ihre Präsentation passt sich jedoch den Ansprüchen und Bedürfnissen der Zielgruppe an.'),
(15, 'Jugendfilm', 'Zielgruppe', NULL, NULL, 'Ein Begriff für Filme, die sich vorrangig an Jugendliche – das heißt Menschen in der Lebensphase zwischen beginnender Pubertät und Erwachsensein – wenden. Jugendfilme im engeren Sinn haben jugendliche Hauptfiguren, die den gleichaltrigen Zuschauern eine mehr oder weniger umfassende Identifikation erlauben, und befassen sich mit Themen, die im Leben von Jugendlichen eine besondere Rolle spielen, also etwa emotionales, sexuelles und körperliches Erwachsenwerden, allmähliche Ablösung von den Eltern, Freundschaft und erste Liebe.'),
(16, 'Familienfilm', 'Zielgruppe', NULL, NULL, 'Ein Begriff für Filme, bei denen im Gegensatz zum Kinderfilm auch Erwachsene als Zuschauer miteinbezogen werden. Es werden Handlungsebenen für Erwachsene eingebunden, ohne die Kinder als Zuschauer zu langweilen. Der Begriff des Familienfilms ist dabei erst in den 1990er-Jahren aufgetaucht, um die Einordnung als Kinderfilm bei der Vermarktung von Filmen zu vermeiden. Kinderfilme mussten früher mit niedrigen Budgets auskommen und wurden dementsprechend häufig als wenig attraktiv angesehen. Außerdem sollte Erwachsenen als möglichen Begleitpersonen von Kindern vermittelt werden, dass bei der Produktion eines Films auch ihre Interessen berücksichtigt werden, um diese als zusätzliche Zuschauer zu gewinnen. Identifikationsfiguren bieten dort oft Fantasiefiguren oder Erwachsene in Rollen, in denen Kinder über sie lachen können.'),
(17, 'Family Entertainment', 'Zielgruppe', NULL, 16, 'Alternativer Begriff für Familienfilm.'),
(18, 'Frauenfilm', 'Zielgruppe', NULL, NULL, 'Im engeren Sinne ein Begriff für Filme, die ihre Themen aus weiblichem Blickpunkt behandeln. Der Frauenfilm wurde seit der Mitte der 1970er-Jahre von Regisseurinnen wie Margarethe von Trotta geprägt und beinhaltet oft eine emanzipatorische Zielsetzung. Er wendet sich vorwiegend an ein weibliches Publikum.'),
(19, 'Expressionistischer Film', 'Stilrichtung', NULL, NULL, 'Eine Stilrichtung des Films, die im Wesentlichen in Deutschland entstand, speziell in dessen „Filmhauptstadt“ Berlin, in der Stummfilmzeit der ersten Hälfte der 1920er-Jahre. Oft spricht man deshalb auch vom Deutschen Expressionismus. Charakteristisch sind die stark von der expressionistischen Malerei beeinflussten grotesk verzerrten Kulissen und die kontrastreiche Beleuchtung, die durch gemalte Schatten noch unterstützt wurde. Durch eine surrealistische und symbolistische mise-en-scène werden starke Stimmungen und tiefere Bedeutungsebenen erzeugt. Daneben ist es aber vor allem die betont übertrieben gestische Spielweise der Darsteller, die das Expressionistische dieser Filmströmung kennzeichnet. Sie ist dem künstlerischen Vorläufer, dem Bühnenexpressionismus entlehnt.'),
(20, 'Film noir', 'Stilrichtung', NULL, NULL, 'Der Begriff Film noir bezeichnet ein Filmgenre oder – je nach Sichtweise – eine Stilrichtung des Films. Seine klassische Ära hatte der Film noir in den Vereinigten Staaten der 1940er und 1950er Jahre. Er ist gekennzeichnet durch eine pessimistische Weltsicht, düstere Bildgestaltung und entfremdete, verbitterte Charaktere.'),
(21, 'Italienischer Neorealismus', 'Stilrichtung', NULL, NULL, 'Der Italienische Neorealismus bezeichnet eine bedeutende Epoche der Filmgeschichte und der Literatur von 1943 bis etwa 1954. Der Neorealismus, auch Neorealismo oder Neoverismo genannt, entstand noch während der Zeit des italienischen Faschismus unter der Diktatur Mussolinis und wurde von italienischen Literaten, Filmautoren und Regisseuren begründet, darunter Roberto Rossellini, Luigi Zampa, Luchino Visconti, Federico Fellini, Vittorio De Sica. Der Neorealismus war eine Antwort auf den Faschismus in Italien, künstlerisch vom Poetischen Realismus Frankreichs beeinflusst, aber auch politisch durch den Marxismus motiviert. Die ersten Filme dieses Stils entstanden noch während der Zeit, in der das Land im Norden von den Deutschen und im Süden von den Alliierten besetzt war. Die Filme des Neorealismus sollten die ungeschminkte Wirklichkeit zeigen, das Leiden unter der Diktatur, Armut und Unterdrückung des einfachen Volkes. Der Neorealismus ist in erster Linie ein „moralischer Begriff“, so Roland Barthes, der „genau das als Wirklichkeit darstellt, was die bürgerliche Gesellschaft sich bemüht zu verbergen“.'),
(22, 'New Hollywood', 'Stilrichtung', NULL, NULL, 'New Hollywood bezeichnet US-amerikanische Filme, die ab 1967 bis Ende der 1970er Jahre das traditionelle Hollywood-Kino modernisierten. Als Vorläufer des New Hollywood entstanden noch im klassischen Studiosystem mit Die Reifeprüfung\" und \"Bonnie und Clyde\" zwei Filme, die sich formal wie thematisch von den bis dato gängigen Hollywood-Produktionen unterschieden und damit sehr erfolgreich waren. Nahezu alle New-Hollywood-Filme zeichnen sich durch eine gesellschaftskritische Grundhaltung aus. Viele stellen in einer radikalen, ungewohnt deutlichen Weise Sex und Gewalt dar. Einige Regisseure modernisierten die klassischen Genres des Hollywood-Kinos (Western, Film noir etc.) oder dekonstruierten sie, indem sie absichtlich gegen Genre-Konventionen verstießen. Typisch für New Hollywood sind inhaltliche oder filmästhetische Experimente mit ambivalenten Außenseitern als Protagonisten, der Bruch mit traditionellen Erzählweisen und der Verzicht auf ein Happy End. Die relativ kurze New-Hollywood-Ära gilt als eine der künstlerisch bedeutendsten Phasen des amerikanischen Films.'),
(23, 'Nouvelle Vague', 'Stilrichtung', NULL, NULL, 'Nouvelle Vague (frz.: „Neue Welle“) ist eine Stilrichtung, die im französischen Kino der späten 1950er Jahre entstand. Sie wandte sich gegen die eingefahrene Bildsprache und den vorhersagbaren Erzählfluss des etablierten kommerziellen Kinos und forderte vom Regisseur, sich an allen Schritten der Filmproduktion zu beteiligen, um so einen eigenen persönlichen Stil entwickeln zu können. Mit dieser charakteristischen Handschrift des Regisseurs sollten die Filme persönlicher und individueller werden und aus dem Schattendasein der Literatur treten.'),
(24, 'Poetischer Realismus', 'Stilrichtung', NULL, NULL, 'Der Poetische Realismus entstand im französischen Kino und war geprägt durch die wirtschaftliche Krise Anfang der 1930er Jahre. Angetrieben vom Drang nach mehr Realitätsnähe und Sozialkritik, kehrten einige junge Regisseure bewusst der französischen Avantgarde den Rücken. Trotz der widrigen Umstände der damaligen Zeit und einer brachliegenden Filmindustrie gelang es diesen Filmregisseuren in Zusammenarbeit mit dem Drehbuchautor Jacques Prévert und dem Szenenbildner Alexandre Trauner, Filmgeschichte zu schreiben. Der Poetische Realismus bereitete den später in Italien entstandenen Neorealismus maßgeblich vor.'),
(25, 'British New Wave', 'Stilrichtung', NULL, NULL, 'British New Wave bezeichnet einen Filmstil, der hervorgegangen ist aus Filmen junger britischer Regisseure vom Ende der 1950er bis frühen Mitte der 1960er Jahre. Die Filme entstanden ungefähr zeitgleich mit dem Aufkommen der französischen Nouvelle Vague. Thema der Filme ist vor allem das Leben der Arbeiterklasse in Nordengland. Die Filme sind meist in schwarz-weiß gedreht und bemühen sich um einen fast dokumentarischen Realismus.'),
(26, 'Neuer Deutscher Film', 'Stilrichtung', NULL, NULL, 'Der Neue Deutsche Film (auch Junger Deutscher Film, abgekürzt: JDF) war ein Filmstil in der Bundesrepublik Deutschland der 1960er und 1970er Jahre. Prägende Regisseure waren Alexander Kluge, Edgar Reitz, Wim Wenders, Volker Schlöndorff, Werner Herzog, Hans-Jürgen Syberberg, Werner Schroeter und Rainer Werner Fassbinder. Diese Filmemacher stellten Gesellschafts- und politische Kritik in den Mittelpunkt ihrer Arbeit, auch in Abgrenzung zu reinen Unterhaltungsfilmen. Als Autorenfilme wurden diese Produktionen in der Regel unabhängig von großen Filmstudios realisiert. Der Neue Deutsche Film wurde von der französischen „Nouvelle Vague“ und der 68er Protestbewegung beeinflusst.'),
(27, 'New British Cinema', 'Stilrichtung', NULL, NULL, 'Unter dem Begriff New British Cinema werden innovative Strömungen im britischen Kino in den 1980er und 1990er Jahren zusammengefasst. Sie sind geeint in dem Bemühen, die gesellschaftlichen Entwicklungen in Großbritannien seit der Thatcher-Ära zu analysieren und zu kritisieren. Dabei reicht die Bandbreite von realistisch inszenierten Sozialdramen und Komödien über Historienfilme bis hin zu experimentell beeinflusstem Arthouse-Kino.'),
(28, 'Gore', 'Stilmittel', NULL, NULL, 'Als Gore (engl. geronnenes Blut und durchbohren, aufspießen) wird, ähnlich wie beim Splatter, eine visuelle und affektorientierte Strategie der filmischen Körperdarstellung bezeichnet. Während beim Splatter jedoch der Akt des Verletzens im Mittelpunkt steht, wird beim Gore eher das Ergebnis der Gewalt in farbigen, klinisch detaillierten Groß-, Nah- und Detailaufnahmen präsentiert. Zerstückelungen, Ausweidungen, das Herausquellen von Organen sowie das Waten in den Eingeweiden der Filmopfer finden hier ihren Platz. Eine genaue Differenzierung zwischen Splatter und Gore fällt allerdings in den meisten Fällen schwer, oft werden die Begriffe synonym verwendet. Verhältnismäßig häufig wird Gore in Horrorfilmen und Yakuza-Filmen verwendet, aber auch andere Genre spielen mit diesem Stilmittel'),
(29, 'Mindbending', 'Stilmittel', NULL, NULL, 'Mindbending (engl., wörtl. etwa Gedanken-Verbiegen) ist ein Stilmittel das beim Zuschauer Ungewissheit und Spannung durch Desorientierung hervorruft. Die Desorientierung wird gewöhnlich durch Methoden und Tricks wie zum Beispiel nicht-lineares Erzählen, unzuverlässige Standpunkte und radikale Handlungswendungen erreicht. Typischerweise ist der Protagonist solcher Filme verwirrt oder getäuscht in Bezug darauf, was die Realität ist, wobei die Zuschauer gleichermaßen im Dunkeln gehalten werden. Am Ende wird dann entweder (oft in überraschender Weise) Klarheit geschaffen, oder aber das Ende bleibt absichtlich mehrdeutig. Meist ist es so, dass sich einige Sequenzen des Films im Nachhinein als unwirklich herausstellen, zum Beispiel als Traum, virtuelle Realität, psychotische Halluzination oder multiple Persönlichkeitsstörung, gezielte Manipulation durch eine überlegene Macht, ein subjektiver Irrtum des Protagonisten basierend auf einem fehlerhaften Verständnis der eigenen Identität, oder eine andere Erfahrung, die nicht der Realität entspricht'),
(30, 'Spielfilm', 'Gattung', NULL, NULL, 'Eine Gattung von Filmen in denen Schauspieler eine fiktive Handlung darstellen. Spielfilme werden üblicherweise mit den Mitteln der Spielfilmdramaturgie auf der Grundlage eines Drehbuchs gedreht.'),
(31, 'Dokumentarfilm', 'Gattung', NULL, NULL, 'Eine Gattung von Filmen, die sich mit tatsächlichem Geschehen befassen. Es gibt eine große Bandbreite von verschiedenen Dokumentarfilmarten, die sich vom Versuch, ein möglichst reines Dokument zu erschaffen, über die Doku-Soap bis hin zum Doku-Drama erstreckt. Ein weiterer Schritt ist das Nachspielen von Szenen, die so hätten stattfinden können, oder zum Teil auch so stattgefunden haben.'),
(32, 'Experimentalfilm', 'Gattung', NULL, NULL, 'Eine Gattung von Filmen, die in ihren Motiven und in ihrer Inszenierung abseits der Konventionen des Mediums und der Sehgewohnheiten des Publikums auf avantgardistische Weise neue Ausdrucksmöglichkeiten erforschen.'),
(33, 'Avantgardefilm', 'Gattung', NULL, 32, 'Alternativer Begriff für die Filmgattung Experimentalfilm.'),
(34, 'Nachrichtenfilm', 'Gattung', NULL, NULL, 'Eine Gattung von Filmen, die aktuelle Informationen transportieren'),
(35, 'Werbefilm', 'Gattung', NULL, NULL, 'Eine Gattung von kurzen Filmbeiträgen oder Durchsagen, mit denen für eine Ware, eine Marke oder eine Dienstleistung geworben wird. Häufig werden sie von Werbeagenturen im Auftrag eines Markeninhabers oder Produktanbieters entworfen.'),
(36, 'Werbespot', 'Gattung', NULL, 35, 'Alternativer Begriff für die Filmgattung Werbefilm.'),
(37, 'Wirtschaftsfilm', 'Gattung', NULL, NULL, 'Eine Gattung von Filmen, deren Inhalt und Zweck hauptsächlich wirtschaftlicher, wirtschaftspolitischer oder sozialpolitischer Natur ist.'),
(38, 'Lehrfilm', 'Gattung', NULL, NULL, 'Eine Gattung von Filmen, die für Unterrichtszwecke produziert werden.'),
(39, 'Unterhaltungssendung', 'Gattung', NULL, NULL, 'Eine Gattung von Fernsehsendungen, die hauptsächlich der Unterhaltung dienen.'),
(40, 'Unterrichtsfilm', 'Gattung', NULL, 38, 'Alternativer Begriff für die Filmgattung Lehrfilm.'),
(41, 'Aufklärungsfilm', 'Genre', 31, NULL, 'Filme, die tabuisierte Themen – vornehmlich aus dem Bereich der Sexualität – behandeln'),
(42, 'Bergfilm', 'Genre', 30, NULL, 'Spielfilme, die die Berge oder Bergsportarten in den Mittelpunkt stellen; sowohl der historische, eher heroische Bergfilm als auch neuere Verwendungen des Genres.'),
(43, 'Biographie', 'Genre', 31, NULL, 'Dokumentarfilme, die in fiktionalisierter Form das Leben einer geschichtlich belegbaren Figur erzählen'),
(44, 'Biopic', 'Genre', 31, 43, 'Alternativer Begriff für das Filmgenre Biographie.'),
(45, 'Dokufiktion', 'Genre', 31, NULL, 'Der Begriff Dokufiktion (aus Dokumentation und Fiktion; auch Docufiction oder docu-fiction) bezeichnet eine spekulative oder fiktive Dokumentation. Gewöhnlich dient die Dokufiktion der spektakulären Verbreitung von Wissen über wissenschaftliche Grundprinzipien anhand fiktiver Beispiele. Besonders beliebt ist dieses Format bei der Erklärung der Prinzipien der Evolution, wobei zukünftige oder außerirdische Tiere und Pflanzen bzw. deren Äquivalente nach wissenschaftlichen Prinzipien konstruiert und vorgestellt werden. Es gibt zudem Dokufiktionen, die sich mit mythologischen Wesen, vor allem Drachen beschäftigen. Ebenfalls zu den Dokufiktionen zählen Filme, in denen anstatt echter Aufnahmen gestellte Aufnahmen mit Schauspielern oder solche, die am Computer animiert wurden Verwendung finden. Die Grenzen sowohl zum Dokumentarfilm. als auch zum historischen Spielfilm sind im allgemeinen fließend'),
(46, 'Kulturfilm', 'Genre', 31, NULL, 'Populärwissenschaftliche Dokumentarfilme aus der Zeit zwischen 1918 und 1945, die meist als Beiprogramm zum Hauptfilm in den Kinos gezeigt wurden. Es handelte sich dabei um Lehrfilme zu verschiedensten Sachgebieten wie Naturwissenschaften, Medizin, Kunst, Kultur, Geografie, Geschichte, aber auch um Aufklärungsfilme. In den 1920er Jahren wurde der Begriff zum Teil noch weiter gefasst und schloss auch Verfilmungen klassischer Stoffe ein. Daneben umfasste der Kulturfilm auch Propagandafilme und wurde Teil der nationalsozialistischen Filmpolitik.'),
(47, 'Magazinsendung', 'Genre', 31, NULL, 'Magazinsendungen sind einem bestimmten Themengebiet zugeordnet; sie werden in einheitlicher Weise gestaltet und . werden in regelmäßiger Folge, meist im Wochenrhythmus, ausgestrahlt. Recherchiert und zusammengestellt werden die einzelnen Beiträge einer Sendung durch eine Redaktion. Moderatoren haben die Aufgabe, die einzelnen Reportagen oder Berichte zu verknüpfen und durch geeignete Einleitungen den Einstieg der Zuhörer bzw. Zuseher in das Thema zu erleichtern. Auch kurze Kommentare, Diskussionen oder Studiogespräche können Elemente einer Magazinsendung sein.'),
(48, 'Reportage', 'Genre', 31, NULL, ''),
(49, 'Tierfilm', 'Genre', 31, NULL, 'Dokumentarfilme, in denen Tiere oder ihr Verhalten im Mittelpunkt stehen.'),
(50, 'Wissenschaftsfilm', 'Genre', 31, NULL, 'Filme, die in ihren Inhalten der Wissenschaft und der Forschung dienen.'),
(51, 'Nachrichten', 'Genre', 34, NULL, 'Eine Darbietung von Informationen zu Politik, Wirtschaft, Gesundheit, Forschung, Kultur und Sport und meist einer Wetterprognose.'),
(52, 'Sport', 'Genre', 34, NULL, 'Darstellung sportlicher Ereignisse.'),
(53, 'Antikfilm', 'Genre', 99, 58, 'Alternativer Begriff für das Filmgenre Sandalenfilm.'),
(54, 'Mantel-und-Degen-Film', 'Genre', 99, NULL, 'Abenteuerfilme, in denen akrobatisch choreographierte Degenkämpfe sowie der Widerstand einzelner Protagonisten gegen die Vertreter der staatlichen Obrigkeit oder das Eintreten dieser Protagonisten für Gerechtigkeit oder das Recht auf Freiheit eine zentrale Rolle spielen.'),
(55, 'Piratenfilm', 'Genre', 99, NULL, 'Abenteuerfilme, in denen Piraten, Bukaniere oder Korsaren eine wichtige Rolle spielen, und die typischerweise in der Zeit zwischen dem 17. und 19. Jahrhundert spielen.'),
(56, 'Ritterfilm', 'Genre', 99, NULL, 'Abenteuerfilme, die die Themenwelt des höfischen Mittelalters behandeln und dabei häufig auf Motive der Artus-Epik oder auf Historienromane zurück greifen.'),
(57, 'Samuraifilm', 'Genre', 99, NULL, 'Filme, die das oft tragische Schicksal und den Kampf japanischer Samurai behandeln.'),
(58, 'Sandalenfilm', 'Genre', 99, NULL, 'Abenteuerfilme, die in der Zeit der Antike spielen und mit einem mehr oder weniger großen Aufgebot sandalentragender Komparsen arbeiten.'),
(59, 'Martial-Arts-Film', 'Genre', 202, NULL, 'Eine ursprünglich fernöstliche Variante des Kampfsportfilms.'),
(203, 'Kampfsport', 'Genre', 100, 202, 'Alternativer Begriff für Kampfsportfilm.'),
(60, 'Barbarenfilm', 'Genre', 111, NULL, 'Spielfilme, die in fiktiver mythischer Vorzeit angesiedelt sind und in deren Mittelpunkt ein als Barbar charakterisierter Protagonist steht, wobei sich das Barbarentum der Figur normalerweise nicht auf seine ethische Einstellung bezieht – er ist vielmehr meist von edler Gesinnung –, sondern auf seine Darstellung als Verkörperung von Urgewalt und Kriegertum sowie seiner erbarmungslosen Härte im Kampf mit seinen Feinden.'),
(61, 'Actionkomödie', 'Genre', 112, NULL, 'Eine Mischung aus einem Actionfilm und einer Filmkomödie.'),
(62, 'Commedia all’italiana', 'Genre', 112, NULL, 'Eine Bezeichnung für das Genre der italienischen Filmkomödien der späten 1950er- und 1960er-Jahre. Die Komödien befassten sich - oft mit satirischem Unterton - mit den Gewohnheiten des Bürgertums.'),
(63, 'Culture-Clash-Komödie', 'Genre', 112, NULL, 'Filmkomödien, die vom Zusammenprall unterschiedlicher Kulturen leben.'),
(64, 'Fantasykomödie', 'Genre', 112, NULL, 'Eine Mischung aus einem Fantasyfilm und einer Filmkomödie.'),
(65, 'Gaunerkomödie', 'Genre', 112, 68, 'Alternativer Begriff für das Filmgenre Kriminalkomödie.'),
(66, 'Horrorkomödie', 'Genre', 112, NULL, 'Eine Mischung aus einem Horrorfilm und einer Filmkomödie.'),
(67, 'Krimikomödie', 'Genre', 112, 68, 'Alternativer Begriff für das Filmgenre Kriminalkomödie.'),
(68, 'Kriminalkomödie', 'Genre', 112, NULL, 'Eine Mischung aus einem Kriminalfilm und einer Filmkomödie, in der Handlung steht dabei die Kriminalgeschichte im Vordergrund, sie wird jedoch durch die einzelnen scherzhaften Aktionen oder Dialoge untermalt.'),
(69, 'Lederhosenfilm', 'Genre', 112, NULL, 'Erotikkomödien, typischerweise aus deutscher oder österreichischer Produktion, die  ursprünglich im ländlichen, alpinen Milieu spielen, und deren Komik vom Missverhältnis zwischen äußerlicher Sittsamkeit und überbordender Triebhaftigkeit der Hauptfiguren lebt.'),
(70, 'Musikkomödie', 'Genre', 112, NULL, 'Filmkomödien, in denen das Thema Musik im Mittelpunkt steht.'),
(71, 'Parodie', 'Genre', 112, NULL, 'Eine verzerrende, übertreibende oder verspottende Nachahmung eines Werkes, einer Person, eines ganzen Genres, oder sonstiger Ziele.'),
(72, 'Romantische Komödie', 'Genre', 112, NULL, 'Eine Mischung aus einem Liebesfilm und einer Filmkomödie.'),
(73, 'Romcom', 'Genre', 112, 72, 'Alternativer Begriff für das Filmgenre Romantische Komödie.'),
(74, 'Science-Fiction-Komödie', 'Genre', 112, NULL, 'Eine Mischung aus einem Science-Fiction-Film und einer Filmkomödie.'),
(75, 'Screwball-Komödie', 'Genre', 112, NULL, 'Filmkomödien, die häufig den Krieg der Geschlechter thematisieren und sich im Idealfall durch hohe Dialoglastigkeit, Wortwitz, ein rasantes Tempo und eine raffiniert konstruierte Handlung auszeichneen; Screwball-Komödien erlebten ihren Höhepunkt von Mitte der 1930er bis Anfang der 1940er Jahre.'),
(76, 'Slapstick', 'Genre', 112, NULL, 'Filmkomödien, die ohne Worte auskommen und bei der die Komik durch körperbezogene Aktionen hervorgerufen wird, wie das Ausrutschen auf einer Bananenschale oder das Werfen von Sahnetorten.'),
(77, 'Tragikomödie', 'Genre', 112, NULL, 'Filmkomödien, bei denen das Geschehen in seiner Entwicklung einen unglücklichen Ausgang erwarten ließ, aber überraschend ein gutes Ende nimmt, und zugleich in seiner Art und Weise komisch wirkt.'),
(78, 'Verwechslungskomödie', 'Genre', 112, NULL, 'Filmkomödien, deren besonderer humoristischer Reiz darin besteht, dass Figuren aufgrund ihrer Äußerlichkeiten bzw. ihrer Handlungsweisen mit anderen Personen verwechselt werden und dies zu Verwicklungen führt.'),
(79, 'Western-Komödie', 'Genre', 112, NULL, 'Eine Mischung aus einem Western und einer Filmkomödie.'),
(80, 'Splatterfilm', 'Genre', 115, NULL, 'Filme, bei denen die Darstellung von exzessiver Gewalt und Blut im Vordergrund steht.'),
(81, 'Agentenfilm', 'Genre', 121, 89, 'Alternativer Begriff für das Filmgenre Spionagefilm.'),
(82, 'Gangsterfilm', 'Genre', 121, NULL, 'Kriminalfilme, die durch die Schilderung von illegalen Aktivitäten gekennzeichnet sind, wobei der soziale und/oder psychische Werdegang der Verbrecher, oft im Zusammenhang mit ganzen Verbrecherorganisationen, im Mittelpunkt steht.'),
(83, 'Gefängnisfilm', 'Genre', 121, NULL, 'Kriminalfilme mit einem Gefängnis als Handlungsort, der meistens Ausdruck eines Wandels in der Geschichte der Protagonisten ist: entweder ein Ort der Läuterung oder einer Fortführung der kriminellen Karriere unter den veränderten Bedingungen einer Haftanstalt. Maßgeblich für die handlungsprägende Gefängnissituation sind die Zwangsbedingungen der Haft: Isolation, fehlende Selbstbestimmung und Entmenschlichung.'),
(84, 'Gerichtsfilm', 'Genre', 121, NULL, 'Kriminalfilme, die sich mit der juristischen Auseinandersetzung mit einem zuvor begangenen Verbrechen beschäftigen. Nicht selten ist das Verbrechen an sich auch Bestandteil der Handlung.'),
(85, 'Polizeifilm', 'Genre', 121, NULL, 'Kriminalfilme, bei denen Mitarbeiter der Polizei und ihre Arbeit bei der Lösung von Kriminalfällen im Handlungsmittelpunkt stehen; häufig sind diese Filme aktionsbetont aufgebaut und stellen oft durch das Mittel der Parallelmontage die Tätigkeit von Gesetzeshütern und Kriminellen gegenüber, bis die Handlungsstränge zum Ende des Films zu einem Showdown zusammengeführt werden.'),
(86, 'Serial-Killer-Film', 'Genre', 121, 87, 'Alternativer Begriff für das Filmgenre Serienkillerfilm.'),
(87, 'Serienkillerfilm', 'Genre', 121, NULL, 'Ein Subgenre des Kriminalfilms und kann Elemente des Thrillers, des Polizeifilms oder des Horrorfilms enthalten. Er thematisiert die Taten von Serienmördern und kann sowohl aus der Täterperspektive, als auch aus Opfersicht oder dem Blickpunkt der Ermittler erzählen.'),
(88, 'Serienmörderfilm', 'Genre', 121, 87, 'Alternativer Begriff für das Filmgenre Serienkillerfilm.'),
(89, 'Spionagefilm', 'Genre', 121, NULL, 'Kriminalfilme, die sich mit der Arbeit von Spionen und Geheimagenten beschäftigen. Dramaturgische Kraft beziehen Spionagefilme durch das Doppelleben ihrer Protagonisten. Fragen der Identität, Zweifel am eigenen Wertesystem, der schmale Grat zwischen Täuschung und Selbsttäuschung und die Schwierigkeiten einer entwurzelten Existenz an den Frontlinien internationaler Konflikte sind oft behandelte Themen des Spionagefilms.'),
(90, 'Whodunit-Film', 'Genre', 121, NULL, 'Kriminalfilme, bei denen der Zuschauer anfangs nicht weiß wer der Täter ist, und wo die Ermittlung des Täters eine Rätselmöglichkeit für Zuschauer darstellt. Das Genre ist vor allem im Gegensatz zu einem in der Handlung anders aufgebauten Kriminalfilm zu verstehen, bei dem die Tat und die Täter selbst bereits vor der Aufklärung dem Leser bekannt und verständlich ist oder die Tat selbst die Handlung darstellt.'),
(91, 'Holocaust-Drama', 'Genre', 124, NULL, 'Unter dem Begriff Holocaust-Drama werden Filmdramen zusammengefasst, die das Schicksal einzelner – in der Regel fiktiver Personen – vor dem realen Hintergrund des Holocaust in den deutschen Vernichtungs- und Konzentrationslagern bis 1945 zeigen. Der Begriff wurde vor allem für die Filme in der Nachfolge des sehr erfolgreichen Films Schindlers Liste (1993) ab Mitte der 1990er Jahre verwendet.'),
(92, 'Gesellschafts-Satire', 'Genre', 133, NULL, 'Satiren, in denen die Gesellschaft hauptsächlicher Gegenstand der satirischen Darstellungsweise ist.'),
(93, 'Medien-Satire', 'Genre', 133, NULL, 'Satiren, in denen die Medien hauptsächlicher Gegenstand der satirischen Darstellungsweise sind.'),
(94, 'Mockumentary', 'Genre', 133, NULL, 'Der Begriff Mockumentary (mock: vortäuschen, verspotten\" und documentary: \"Dokumentarfilm\") bezeichnet fiktionale Dokumentarfilme, die echte Dokumentarfilme oder das ganze Genre parodieren. Eine Mockumentary tut so, als sei sie ein Dokumentarfilm, ohne tatsächlich einer zu sein. Dabei werden oft scheinbar reale Vorgänge inszeniert oder tatsächliche Dokumentarteile in einen fiktiven bzw. erfundenen Zusammenhang gestellt. Es ist ein geläufiges filmisches Genremittel für Parodie und Satire. Eine Mockumentary kann außerdem das Ziel haben, ein stärkeres Medienbewusstsein zu schaffen und Zuschauer dazu zu bringen, Medien zu hinterfragen und nicht alles zu glauben, was täglich im Fernsehen zu sehen ist.'),
(95, 'Polit-Satire', 'Genre', 133, NULL, 'Satiren, in denen die Politk hauptsächlicher Gegenstand der satirischen Darstellungsweise ist.'),
(96, 'Apokalypsenfilm', 'Genre', 134, 97, 'Alternativer Begriff für das Filmgenre Endzeitfilm.'),
(97, 'Endzeitfilm', 'Genre', 134, NULL, 'Science-Fiction-Filme, in denen die Filmhandlung in einer durch eine globale Katastrophe radikal veränderten Weltordnung situiert ist.'),
(98, 'Postapokalyptischer Film', 'Genre', 134, 97, 'Alternativer Begriff für das Filmgenre Endzeitfilm.'),
(99, 'Abenteuerfilm', 'Genre', 30, NULL, 'Spielfilme, in denen die Protagonisten in eine ereignisreiche Handlung, mitunter mit vielen Schauplatzwechseln, verstrickt sind, wobei im Vordergrund nicht die Entwicklung der Charaktere an sich steht, sondern die diese Entwicklung hervorrufenden Ereignisse.'),
(100, 'Actionfilm', 'Genre', 30, NULL, 'Spielfilme, in denen der Fortgang der Handlung von zumeist spektakulär inszenierten Kampf- und Gewaltszenen vorangetrieben und illustriert wird, meist mit aufwändig gedrehten Stunts, Schlägereien, Schießereien, Explosionen und Verfolgungsjagden.'),
(101, 'Anthologiefilm', 'Genre', 30, 108, 'Alternativer Begriff für das Filmgenre Episodenfilm.'),
(102, 'Antikriegsfilm', 'Genre', 30, 119, 'Alternativer Begriff für das Filmgenre Kriegsfilm.'),
(103, 'Buddy-Film', 'Genre', 30, NULL, 'Filme mit zwei Hauptcharakteren gleichen Geschlechts. Die Akteure sind durch ein zwischenmenschliches Verwandtschafts- oder Bekanntschaftsverhältnis, ein Ereignis oder eine Situation zum gemeinschaftlichen Handeln quasi gezwungen, um die Lösung der verbindenden Problematik – meist am Ende der Geschichte – in Teamarbeit erreichen zu können.'),
(104, 'Cinema Beur', 'Genre', 30, NULL, 'Der Begriff Cinema Beur (cinema: Kino\" und verlan: \"Araber\") bezeichnet Filme, die sich mit Migranten arabischer Herkunft in Frankreich befasst und/oder von einem \"Beur\" geschaffen wurde bzw. das die \"Beurs\" als Zielgruppe avisiert.'),
(105, 'Desasterfilm', 'Genre', 30, 116, 'Alternativer Begriff für das Filmgenre Katastrophenfilm.'),
(106, 'Drama', 'Genre', 30, 124, 'Alternativer Begriff für das Filmgenre Melodram.'),
(107, 'Eastern', 'Genre', 30, NULL, 'Spielfilme, in denen Asiatisches und Östlich-Orientalisches mit Stilmerkmalen des amerikanischen Genrekinos zusammentrifft, speziell mit Stilmerkmalen des Western (daher auch die rhetorische Analogie).'),
(108, 'Episodenfilm', 'Genre', 30, NULL, 'Ein Begriff für Spielfilme, die aus einer Anzahl abgeschlossener Kurzfilme von einem oder mehreren Regisseuren bestehen. Die Episoden stehen in der Regel unter einem gemeinsamen Thema oder weisen Berührungspunkte auf. Möglich ist auch eine übergreifende Rahmenhandlung. Durchgehende Handlungsstränge sind dagegen unüblich.'),
(109, 'Erotikfilm', 'Genre', 30, NULL, 'Filme, in denen die Darstellung menschlicher Sexualität im Mittelpunkt steht.'),
(110, 'Exploitationfilm', 'Genre', 30, NULL, 'Filme, die reißerische Grundsituationen ausnutzen, um mittels der exploitativen Darstellung vornehmlich von Sex und Gewalt über die damit erreichten Schauwerte affektiv auf den Zuschauer zu wirken. Merkmale des Exploitationfilms sind die oft subversiven Veränderungen der Vorbilder, besonders im Italo- oder Spaghettiwestern, in denen der Held oft genauso verkommen ist wie seine Gegenspieler („Django“, 1966), sowie die reißerische Anreicherung mit Sex und Gewalt, Blasphemie, Kirchenkritik, Hexenverfolgung und Nationalsozialismus. Charakteristisch ist in der Regel auch die Titel- bzw. Untertitelwahl, die oft bemüht ist, das Vorhandensein der jeweiligen Elemente zu Werbezwecken zu betonen oder sogar zu übertreiben (z. B. „Nonnen bis aufs Blut gequält“, 1974).'),
(111, 'Fantasyfilm', 'Genre', 30, NULL, 'Spielfilme, deren Handlung Elemente enthalten, welche nur in der menschlichen Fantasie existieren und in der Realität eigentlich so nicht vorstellbar sind. Eng verwandt ist der Märchenfilm; die meisten Märchenfilme sind gleichzeitig Fantasyfilme, aber nicht alle Fantasyfilme sind Märchenfilme.'),
(112, 'Filmkomödie', 'Genre', 30, NULL, 'Spielfilme mit einem erheiternden Handlungsablauf, der in der Regel glücklich endet. Die unterhaltsame Grundstimmung entsteht häufig durch eine übertriebene Darstellung menschlicher Schwächen, die neben der Belustigung des Publikums auch kritische Zwecke haben kann.'),
(113, 'Heimatfilm', 'Genre', 30, NULL, 'Spielfilme, in dem es um Freundschaft, Liebe, Familie und um das Leben in der dörflichen Gemeinschaft geht, und die oft eine heile Welt darstellen.'),
(114, 'Historienfilm', 'Genre', 30, NULL, 'Spielfilme, deren Inhalt auf historischen Figuren, Ereignissen oder Bewegungen basiert, oder der eine in einen historischen Kontext eingebettete fiktive Erzählung ist.'),
(115, 'Horrorfilm', 'Genre', 30, NULL, 'Spielfilm, deren Handlung beim Zuschauer Gefühle der Angst, des Schreckens und Verstörung auszulösen versucht. Oftmals, jedoch nicht zwangsläufig, treten dabei übernatürliche Akteure oder Phänomene auf, von denen eine zumeist lebensbedrohliche und traumatische Wirkung auf die Protagonisten ausgeht.'),
(116, 'Katastrophenfilm', 'Genre', 30, NULL, 'Spielfilme, die von einem allumfassenden Unglück, meist einer Naturkatastrophe oder einer Katastrophe, die im Zusammenhang mit technischem Fortschritt steht, handeln. Stilbildendes Element ist ein einzelner, meist einfacher Mensch der angesichts der drohenden Katastrophe über sich hinauswächst und unter persönlichen Verlusten wesentlich zur Überwindung der Krise beiträgt.'),
(117, 'Kifferfilm', 'Genre', 30, NULL, 'Spielfilme, in deren Handlung der Konsum von Cannabis- oder Haschisch-Drogen eine grundlegende Bedeutung hat.'),
(118, 'Knockbuster', 'Genre', 30, NULL, 'Der Begriff Knockbuster (Verkürzung von knock-off-Blockbuster), bezeichnet Filme, die eine trashige Kopie eines meist zur gleichen Zeit erscheinenden Blockbusters darstellen. Siehe auch Mockbuster. Während bei einem Mockbuster-Film eher die Parodie des Originals in Titel und Handlung im Vordergrund steht, versucht ein Knockbuster nur eine möglichst billige und besonders trashige Kopie zu sein.'),
(119, 'Kriegsfilm', 'Genre', 30, NULL, 'Spielfilme, in denen die kriegerischen Auseinandersetzungen den Hintergrund für die handelnden Personen abgeben und deren Handlungsstränge ganz oder zum großen Teil in einem Kriegsszenario verlaufen.'),
(120, 'Krimi', 'Genre', 30, 121, 'Alternativer Begriff für das Filmgenre Kriminalfilm.'),
(121, 'Kriminalfilm', 'Genre', 30, NULL, 'Spielfilme, bei denen ein Verbrechen oder dessen Aufklärung oder die daran beteiligten Charaktere im Mittelpunkt stehen.'),
(122, 'Liebesfilm', 'Genre', 30, NULL, 'Spielfilme, deren hauptsächliches Thema die Liebe zwischen zwei Menschen ist. Erfüllt sich diese Liebe in einem Happy End, stehen die romantischen Aspekte der Geschichte im Vordergrund. Bleibt die Liebe unerfüllt, hat der Liebesfilm einen melodramatischen Charakter.'),
(123, 'Märchenfilm', 'Genre', 30, NULL, 'Spielfilme, die von magischen Abenteuern von sagenhaften Prinzen und Prinzessinnen, Feen, Zauberern, Zwergen, Hexen, Drachen, Trollen, Riesen, Kobolden, Nixen, Wassermänner und anderen märchenhaften Wesen handeln. Wichtig sind auch zauberische Gegenstände wie Siebenmeilenstiefel, Tarnkappe, Zauberspiegel, Zaubernüsse, Tischlein deck dich und Wünschelruten. Märchenfilme changieren zwischen Kinderfilm, Literaturfilm und Fantasyfilm – in den gelungensten Fällen sind sie eine Synthese dieser Aspekte.'),
(124, 'Melodram', 'Genre', 30, NULL, 'Spielfilme, in denen der Inhalt die Form dominiert und die Charaktere der Protagonisten ausführlich dargestellt werden, und in dem häufig der Kampf Gut gegen Böse das Grundmotiv ist, oft mit einer Liebesgeschichte als Grundthema.'),
(125, 'Mockbuster', 'Genre', 30, NULL, 'Der Begriff Mockbuster (Verkürzung von mock-up-Blockbuster), bezeichnet Filme, die eine Parodie oder Verulkung eines meist zur gleichen Zeit erscheinenden Blockbusters darstellen. Siehe auch Knockbuster. Während bei einem Mockbuster-Film eher die Parodie des Originals in Titel und Handlung im Vordergrund steht, versucht ein Knockbuster nur eine möglichst billige und besonders trashige Kopie zu sein.'),
(126, 'Mystery-Film', 'Genre', 30, NULL, 'Spielfilme, in denen es um vermeintliche übernatürliche Phänomene geht, deren Darstellung eine Affinität zu Ambivalenz, Zwiespältigkeit und Undurchsichtigkeit aufweisen.'),
(127, 'Omnibusfilm', 'Genre', 30, 108, 'Alternativer Begriff für das Filmgenre Episodenfilm.'),
(128, 'Phantastischer Film', 'Genre', 30, 111, 'Alternativer Begriff für das Filmgenre Fantasyfilm.'),
(129, 'Pornofilm', 'Genre', 30, 109, 'Alternativer Begriff für das Filmgenre Erotikfilm.'),
(130, 'Revuefilm', 'Genre', 30, NULL, 'Der Revuefilm ist ein deutsches Filmgenre und eng verwandt mit dem Musical, der Operette und dem Tanzfilm. Der Begriff wird vor allem für deutsche und österreichische Musik- und Tanzfilme angewandt, die im Zeitraum der 1930er bis 1950er Jahre entstanden sind. Die Filme zeichnen sich durch leichte, beschwingende, fröhliche Unterhaltung aus, gespickt mit immer wiederkehrenden Gesangs- und Tanzeinlagen, vorwiegend bestehend aus zeitgenössischen Schlagerhits. Die Handlung baut meist auf einer romantischen Komödie auf, in der es oft um Backstage-Proben oder Aufführungen von Revuen geht. Der Revuefilm kann außerdem (muss aber nicht) eine verfilmte Revue eines Musiktheaters sein. Der Revuefilm hatte im Nationalsozialismus seine größte Popularität, danach wurde er allmählich vom Schlagerfilm abgelöst.'),
(131, 'Roadmovie', 'Genre', 30, NULL, 'Spielfilme, deren Handlung auf Landstraßen und Highways spielen; dabei wird die Reise zur Metapher für die Suche nach Freiheit und Identität der Protagonisten.'),
(132, 'Romanze', 'Genre', 30, 122, 'Alternativer Begriff für das Filmgenre Liebesfilm.'),
(133, 'Satire', 'Genre', 30, NULL, 'Spielfilme, in denen die satirische Darstellungsweise ein maßgebendes Element ist.'),
(134, 'Science-Fiction-Film', 'Genre', 30, NULL, 'Spielfilm, die sich mit fiktionalen Techniken sowie wissenschaftlichen Leistungen und deren möglichen Auswirkungen auf die Zukunft beschäftigen.'),
(135, 'Sexfilm', 'Genre', 30, 109, 'Alternativer Begriff für das Filmgenre Erotikfilm.'),
(136, 'Sittenfilm', 'Genre', 30, NULL, 'Filme, die unter dem Mantel der Aufklärung tabuisierte Themen, meist aus dem Bereich der Sexualität, behandeln.Im Mittelpunkt steht dabei nicht die Freude an der Sexualität, sondern die Zwänge und die Gewalt, die sie auf Menschen ausübt. Auch wenn der Sittenfilm oft mit dem Aufklärungsfilm gleich gesetzt wird, unterscheidet er sich von diesem durch seinen exploitativen Charakter und die primär voyeuristische Zielrichtung der Inhalte. Das Filmgenre der Sittenfilme diente der erotischen Unterhaltung und erlebte in Deutschland seinen Höhepunkt ab etwa 1918, begünstigt durch die Tatsache, dass es zwischen November 1918 und Mai 1920 keine Filmzensur gab. Gegen Ende der 1920er-Jahre erlebte das Genre eine kurze Renaissance.'),
(137, 'Sportfilm', 'Genre', 30, NULL, 'Spielfilme, in denen Sportler, Sportarten oder sportliche Ereignisse im Mittelpunkt der Handlung stehen.'),
(138, 'Stoner-Movie', 'Genre', 30, 117, 'Alternativer Begriff für das Filmgenre Kifferfilm.'),
(139, 'Thriller', 'Genre', 30, NULL, 'Spielfilme, bei denen die Spannung nicht nur in kurzen Passagen, sondern fast während des gesamten Handlungsverlaufs präsent ist. Thriller überschneiden sich mit dem Mystery-Genre sowie dem Kriminalfilm, unterscheiden sich hiervon jedoch anhand ihrer Handlungen und Spannungskurven. In Thrillern muss sich der Held meist gegen moralische, seelische oder physische Gewalteinwirkung durch seinen Gegenspieler behaupten, während dies in Kriminalgeschichten viel weniger der Fall ist. Auch ist im Kriminalroman meist die Aufklärung des Verbrechens der Höhepunkt, während im Thriller erst der darauf folgende, oft sehr knappe, aber endgültige, Sieg über den Widersacher den Höhepunkt darstellt, mit dem der Held sich selbst und womöglich auch andere rettet. In Thrillern, die durch Film noir oder Tragödien beeinflusst wurden, stirbt der Held oft auch beim Besiegen seines Gegners.'),
(140, 'Tierspielfilm', 'Genre', 30, NULL, 'Spielfilme, bei denen Erlebnisse von und mit bestimmten Tieren im Mittelpunkt stehen.'),
(141, 'Trashfilm', 'Genre', 30, NULL, 'Ein Begriff, der für Filme qualitativ schlechter Machart mit geringem Budget verwendet wird. Merkmale, die einen Film als Trashfilm einstufen lassen, sind etwa sehr schlechte Schauspielerei, karge und unecht wirkende Ausstattung, billige Spezialeffekte, bei denen der wahre Verursacher der Simulation zu erkennen ist, sowie unlogische Handlungsstränge mit platten Dialogen. Es gibt auch Filme, die diese Merkmale absichtlich als Stilmittel benutzen. Während Trashfilme auch von Personen geschaut werden, die einen qualitativ mit einer Mainstreamproduktion gleichzusetzenden Film erwarten, findet das Genre vor allem großen Anklang bei einer Zuschauergruppe, die Trashfilme aus einer ironischen Distanz betrachten und sich über den Dilettantismus amüsieren.'),
(142, 'Weihnachtsfilm', 'Genre', 30, NULL, 'Filme, die das Motiv Weihnachten und die damit verbundenen Bräuche zum hauptsächlichen Inhalt haben oder als Zeitschema verwenden.'),
(143, 'Western', 'Genre', 30, NULL, 'Spielfilme, in deren Mittelpunkt der zentrale US-amerikanische Mythos der Eroberung des (wilden) Westens der Vereinigten Staaten im neunzehnten Jahrhundert steht.'),
(144, 'Wiener Film', 'Genre', 30, NULL, 'Ein Filmgenre, das im Wesentlichen eine Verknüpfung der Genres Komödie, Liebesfilm, Melodram und Historienfilm darstellt. Als eigenes Genre abgrenzen lässt er sich aber durch die Tatsache, dass immer das historische Wien samt seinem spezifischen Milieu das Kernelement bilden. Der Wiener Film als Genre bestand zwischen den 1920er- und den 1950er-Jahren, wobei die 1930er-Jahre seinen Höhepunkt darstellten.'),
(145, 'Zirkusfilm', 'Genre', 30, NULL, 'Filme, die das Motiv Zirkus zum hauptsächlichen Inhalt haben.'),
(146, 'Giallo', 'Genre', 139, NULL, 'Der Begriff Giallo (ital. für gelb) bezeichnet ein spezifisches italienisches Subgenre des Thrillers, das von Mario Bava in den 1960ern begründet wurde und in den 1970ern seinen Höhepunkt hatte. Die Handlung dreht sich zumeist um die Aufdeckung einer Mordserie. In der Inszenierung werden vor allem detaillierte Mordszenen und Spannungsszenen durch stilvolle Kameraführung, Ausstattung und Musik betont.'),
(147, 'Heist-Movie', 'Genre', 139, NULL, 'Thriller, die sich mit der Planung, Vorbereitung und Durchführung eines meist spektakulären Raubes befassen, wobei die Handlung aus dem Blickwinkel des Räubers bzw. der Räuber gezeigt wird, die in der Regel auch Sympathieträger sind.'),
(148, 'Politthriller', 'Genre', 139, NULL, 'FIlme, in denen Elemente des Thrillers mit Handlungen verknüpft werden, die in der Politik angesiedelt sind. Der Politthriller unterscheidet sich vom klassischen Thriller dadurch, dass sich die Handlung der Geschichte mit Verwicklungen auf staatlicher Ebene, mit terroristischen Anschlägen, Spionage oder kriminellen Machenschaften staatlicher Institutionen oder deren Vertretern beschäftigt. Dies geschieht durch Einarbeitung von fiktiven politischen Ereignissen, die in existierenden oder fiktiven Ländern stattfinden. Die dargestellten Ereignisse nehmen mitunter Bezug auf reale politische Ereignisse der Vergangenheit.'),
(149, 'Psychothriller', 'Genre', 139, NULL, 'Thriller, bei denen der Konflikt, der sich zwischen den Hauptfiguren entfaltet, eher geistig oder emotional ist als physisch.'),
(150, 'Eurowestern', 'Genre', 143, 151, 'Alternativer Begriff für das Filmgenre Italowestern.'),
(151, 'Italowestern', 'Genre', 143, NULL, 'Western, die vor allem in den 1960er Jahren von italienischen Produktionsfirmen und Regisseuren an europäischen Drehorten produziert wurden. Der klassische, amerikanische Westernfilm wurde durch Italowestern sowohl persifliert als auch weiterentwickelt. An die Stelle moralisierender und traditioneller (US-amerikanischer) Western-Motive wie Aufrichtigkeit, Ritterlichkeit und Altruismus setzte der Italowestern Antihelden, die gegen bürgerliche Konventionen und Verhaltensnormen rebellieren. Auch wurden gesellschaftliche Missstände thematisiert. Ein weiteres wichtiges Motiv war die Darstellung teilweise exzessiver Gewalt.'),
(152, 'Spaghettiwestern', 'Genre', 143, 151, 'Alternativer Begriff für das Filmgenre Italowestern.'),
(153, 'Spätwestern', 'Genre', 143, NULL, 'Vornehmlich US-amerikanische Western, die von den idealisierenden und moralisierenden Motiven des klassischen Westerns abweichen und ein kritisches und/oder pessimistisches Bild der Zeit des Wilden Westens zeichnen.'),
(154, 'Britcom', 'Genre', 164, NULL, 'Als Britcom wird eine britische Sitcom bezeichnet, die im Fernsehen ausgestrahlt wird. Die Britcom wird häufig als düsterer, realistischer und sozialkritischer beschrieben als vergleichbare Comedy-Sendungen aus den USA. Britcoms sind auch formal anders strukturiert als US-amerikanischen Sitcoms, so haben sie pro Staffel oft nur sechs Episoden.'),
(155, 'Impro-Comedy', 'Genre', 164, NULL, 'Comedy-Shows, bei denen zuvor nicht einstudierte Szenen gespielt werden. Meist lassen sich die Schauspieler ein Thema oder einen Vorschlag aus dem Publikum geben. Diese Vorschläge sind dann Auslöser und Leitfaden für die daraufhin spontan entstehenden Szenen. Eine Geschichte entsteht aus der Spontaneität und gegenseitigen Inspiration der Schauspieler.'),
(156, 'Mixed-Comedy-Show', 'Genre', 164, NULL, 'Comedy-Shows in denen diverse Comedians kurz hintereinander auftreten.'),
(157, 'Nummernkomödie', 'Genre', 164, 160, 'Alternativer Begriff für das Filmgenre Stand-up-Comedy.'),
(158, 'Sitcom', 'Genre', 164, NULL, 'Filme, die gekennzeichnet sind duch die humorvolle Auseinandersetzung mit einer momentan vorliegenden Situation durch einen Beteiligten. Ein Kennzeichen der Sitcom ist daher die ständige, schnelle Abfolge von Gags, Pointen und komischen Momenten, allerdings im Rahmen einer dramatischen Handlung, womit sich die Sitcom von Comedyshows unterscheidet, bei denen Sketche lediglich aneinandergereiht werden. Eher selten bekommt die Serie ein bewusst dramatisches Element.'),
(159, 'Sketch', 'Genre', 164, NULL, 'Filme, dier eine kurze komödiantische Szene darstellen, die einer reduzierten Handlung folgt und mit einer prägnanten Schlusspointe abschließt.'),
(160, 'Stand-up-Comedy', 'Genre', 164, NULL, 'Unterhaltungssendungen mit einem überwiegend gesprochenen Solovortrag eines Comedians bzw. Komikers als Kurzauftritt oder auch als abendfüllendes Programm. Inhaltlich unterscheidet sich die Stand-up-Comedy vom Kabarett vor allem durch die innere Haltung des Comedians gegenüber seinen erzählten Geschichten. Während Kabarettisten vorwiegend ihre pointierte Sichtweise des Weltgeschehens schildern, beschreiben Stand-up-Comedians eher ihre eigenen, komischen Konflikte mit der Welt. Heutzutage sind die Grenzen zwischen Stand-up-Comedy und Kabarett oft fließend.'),
(161, 'Trick-Comedy', 'Genre', 164, NULL, 'Comedy-Filme als Trickfilm.'),
(162, 'Konzertmitschnitt', 'Genre', 171, NULL, 'Mitschnitt einer musikalischen Darbietung.'),
(163, 'Musical', 'Genre', 171, NULL, 'Filme, in denen Gesang und meist auch Tanz ein maßgebendes Element ist.'),
(164, 'Comedy', 'Genre', 39, NULL, 'Der Begriff Comedy wird vielfältig für zahlreiche Formen verwandt, denen lediglich der humoristische Charakter gemeinsam ist.'),
(165, 'Game-Show', 'Genre', 39, 169, 'Alternativer Begriff für das Filmgenre Spiel-Show.'),
(166, 'Panel-Show', 'Genre', 39, 167, 'Alternativer Begriff für das Filmgenre Quiz-Show.'),
(167, 'Quiz-Show', 'Genre', 39, NULL, 'Unterhaltungssendungen, in denen Kandidaten Quizaufgaben lösen müssen, die von einem Spielleiter gestellt werden.'),
(168, 'Reality-TV', 'Genre', 39, NULL, 'Unterhaltungssendungen, in denen vorgeblich oder tatsächlich versucht wird, die Wirklichkeit abzubilden, häufig den Alltag in Ausnahmesituationen.'),
(169, 'Spiel-Show', 'Genre', 39, NULL, 'Unterhaltungssendungen in denen einer oder mehrere Kandidaten Aufgaben erfüllen, Rätsel lösen oder Fragen richtig beantworten müssen.'),
(170, 'Talk-Show', 'Genre', 39, NULL, 'Unterhaltungssendungen in Form eines Gesprächs zwischen einem Gastgeber und einem oder mehreren Gesprächsgästen, oder als Diskussion zu einem gegebenen Thema unter den Gesprächsgästen selbst, wobei der Gastgeber als Moderator fungiert.'),
(171, 'Musikfilm', 'Genre', NULL, NULL, 'Filme, in denen das Thema Musik im Mittelpunkt steht.');
INSERT INTO `Genre` (`idGenre`, `Name`, `idGenreType`, `idParentGenre`, `idSynonymOfGenre`, `Description`) VALUES
(172, 'Business TV', 'Genre', 37, 173, 'Alternativer Begriff für das Filmgenre Corporate TV.'),
(173, 'Corporate TV', 'Genre', 37, NULL, 'Fernsehprogramme, die im Rahmen der Unternehmenskommunikation produziert und ausgestrahlt werden.'),
(174, 'Gebrauchsfilm', 'Genre', 37, NULL, 'Sprachfreie oder spracharme interaktive Anleitungsfilme, die aus einzelnen, miteinander verlinkten Videoclips bestehen und hauptsächlich die Bereiche technische Dokumentation, Montage und Schulung abdecken.'),
(175, 'Imagedokumentation', 'Genre', 37, NULL, 'Eine filmische Begleitung eines Projekts, die das Vorhaben eines öffentlichen Trägers, Unternehmens oder Vereins vom Anfang bis zum Ende authentisch porträtiert.'),
(176, 'Imagefilm', 'Genre', 37, NULL, 'Kurze Filme, die in werbender Absicht ein Unternehmen, eine Institution, eine Marke oder ein Produkt portraitieren.'),
(177, 'Unternehmensfilm', 'Genre', 37, 173, 'Alternativer Begriff für das Filmgenre Corporate TV.'),
(178, 'Utility-Film', 'Genre', 37, 174, 'Alternativer Begriff für das Filmgenre Gebrauchsfilm.'),
(179, 'Abenteuer', 'Genre', 30, 99, 'Alternativer Begriff für Abenteuerfilm.'),
(180, 'Krieg', 'Genre', 30, 119, 'Alternativer Begriff für Kriegsfilm.'),
(181, 'Komödie', 'Genre', 30, 112, 'Alternativer Begriff für Filmkomödie.'),
(182, 'Dokumentation', 'Gattung', NULL, 31, 'Alternativer Begriff für die Filmgattung Dokumentarfilm.'),
(183, 'TV-Film', 'VeroeffentlichungsArt', NULL, 2, 'Alternativer Begriff für die Veröffentlichungsart Fernsehfilm.'),
(184, 'Kinder-/Familienfilm', 'Zielgruppe', NULL, 16, 'Alternativer Begriff für Familienfilm.'),
(185, 'Action', 'Genre', 30, 100, 'Alternativer Begriff für das Filmgenre Actionfilm.'),
(186, 'Fantasy', 'Genre', 30, 111, 'Alternativer Begriff für das Filmgenre Fantasyfilm.'),
(187, 'Horror', 'Genre', 30, 115, 'Alternativer Begriff für das Filmgenre Horrorfilm.'),
(188, 'Mystery', 'Genre', 30, 126, 'Alternativer Begriff für das Filmgenre Mystery-Film.'),
(189, 'Science-Fiction', 'Genre', 30, 134, 'Alternativer Begriff für das Filmgenre Science-Fiction-Film.'),
(190, 'Liebe/Romantik', 'Genre', 30, 122, 'Alternativer Begriff für das Filmgenre Liebesfilm.'),
(191, 'Katastrophen', 'Genre', 30, 116, 'Alternativer Begriff für Katastrophenfilm.'),
(192, 'Erotik', 'Genre', 30, 109, 'Alternativer Begriff für Erotikfilm.'),
(193, 'Animation', 'WeltArt', NULL, 12, 'Alternativer Begriff für Trickfilm.'),
(194, 'Splatter', 'Genre', 115, 80, 'Alternativer Begriff für Splatterfilm.'),
(195, 'Fernsehserie', 'VeroeffentlichungsArt', 2, NULL, 'Eine Abfolge von Filmen für die Fernsehausstrahlung mit festen Figuren oder Themen, die typischerweise eine gleich bleibende Dauer und in jeder Folge eine in sich abgeschlossene Geschichte oder Thematik haben.'),
(196, 'Fernseh-Mehrteiler', 'VeroeffentlichungsArt', 2, NULL, 'Ein Fernsehfilm der aus mehreren Teilen besteht.'),
(197, 'TV-Serie', 'VeroeffentlichungsArt', 2, 195, 'Alternativer Begriff für Fernsehserie.'),
(198, 'TV-Mini-Serie', 'VeroeffentlichungsArt', 2, 196, 'Alternativer Begriff für Fernseh-Mehrteiler.'),
(199, 'Gruselfilm', 'Genre', 30, 115, 'Alternativer Begriff für das Filmgenre Horrorfilm.'),
(200, 'Grusel', 'Genre', 30, 199, 'Alternativer Begriff für Gruselfilm.'),
(201, 'Stummfilm', 'Genre', 30, NULL, 'Ein Spielfilm ohne Tonbegleitung der gespielten Handlung, typischerweise mit musikalischer Untermalung oder einmontierten Texten die die Handlung erzählen oder kommentieren.'),
(202, 'Kampfsportfilm', 'Genre', 100, NULL, 'Ein Actionfilm, angereichert mit artistischen Darbietungen von Kampfkünsten.'),
(204, 'Eisenbahnmagazin', 'Genre', 47, NULL, 'Ein Eisenbahnmagazin ist eine Magazinsendung die sich mit dem Thema Eisenbahn beschäftigt.'),
(205, 'Konzert', 'Genre', 171, NULL, 'Filme, in denen ein musikalisches Ereignis gezeigt wird.'),
(206, 'Anime', 'WeltArt', 12, NULL, 'Ein in Japan produzierter Trickfilm.');

-- --------------------------------------------------------

--
-- Table structure for table `Medium`
--

CREATE TABLE `Medium` (
  `idMedium` int(10) UNSIGNED NOT NULL COMMENT 'Single primary key of the table.',
  `Title` text COLLATE utf8_unicode_ci COMMENT 'Title of the movie (TitleTag if not NULL, otherwise TitleFile).',
  `TitleTag` text COLLATE utf8_unicode_ci COMMENT 'Title of the movie, as stated in the file as a tag. Should be in the indicated language.\nFor series: the series title, some numbering, and the episode title.\nIf not stated there, NULL.',
  `TitleFile` text COLLATE utf8_unicode_ci COMMENT 'Title of the movie, as stated in the file name.\nShould be in the indicated language.\nFor series: the series title, some numbering, and the episode title.',
  `ReleaseYear` year(4) DEFAULT NULL COMMENT 'Release year of the movie (ReleaseYearTag if not NULL, otherwise ReleaseYearFile).',
  `ReleaseYearTag` year(4) DEFAULT NULL COMMENT 'Release year of the movie, as stated in the file as a tag. If not stated there, NULL.',
  `ReleaseYearFile` year(4) DEFAULT NULL COMMENT 'Release year of the movie, as stated in the file name. If not stated there, NULL.',
  `SeriesTitle` text COLLATE utf8_unicode_ci COMMENT 'If the movie is part of a series, the series title as stated in the file name.\nOtherwise, NULL.',
  `EpisodeTitle` text COLLATE utf8_unicode_ci COMMENT 'If the movie is part of a series, the episode title, as stated in the file name.\nOtherwise, NULL.',
  `EpisodeId` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'If the movie is part of a series, the episode ID (season+episode, or running number). Otherwise, NULL.',
  `idMediumType` varchar(30) COLLATE utf8_unicode_ci NOT NULL COMMENT 'Foreign key for the media type, identifying the kind of media representation (e.g. file, DVD).',
  `idCabinet` int(10) UNSIGNED NOT NULL COMMENT 'Foreign key to the media cabinet that stores this movie medium.',
  `idMovie` int(10) UNSIGNED DEFAULT NULL COMMENT 'Foreign key to the movie represented by this movie medium.',
  `idStatus` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Foreign key to the status of the movie medium.\nUsually obtained from file location.',
  `Uncut` tinyint(1) DEFAULT NULL COMMENT 'Indicates whether the movie on the media is uncut (e.g. contains advertisements or content before movie begin or after movie end).\nUsually obtained from file name.',
  `Language` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Language(s) of the audio stream in the movie on the medium, as a 2/3-character ISO language code in lower case. Multiple langage strings are separated with ''+''.',
  `SubtitleLanguage` varchar(3) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Language of any subtitles in the movie on the medium, as a 2/3-character ISO language code. in lower case. Null indicates there are no subtitles.',
  `Duration` int(11) DEFAULT NULL COMMENT 'Duration of the movie on the medium, in minutes.',
  `idQuality` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Foreign key for the video quality of the movie on the media.\nUsually obtained from file name.',
  `DesiredDisplayAspectRatioWidth` int(10) UNSIGNED DEFAULT NULL COMMENT 'Width of desired display aspect ratio.\nFor example, 16 for 16:9.\nUsually obtained from file name.',
  `DesiredDisplayAspectRatioHeight` int(11) DEFAULT NULL COMMENT 'Height of desired display aspect ratio.\nFor example, 9 for 16:9.\nUsually obtained from file name.',
  `DisplayAspectRatio` float DEFAULT NULL COMMENT 'Display aspect ratio field of video stream in medium.\nMost video players give the original DAR field precedence over this field.',
  `OriginalDisplayAspectRatio` float DEFAULT NULL COMMENT 'Original display aspect ratio field of video stream in medium.\nMost video players give this field precedence over the display aspect ratio field.',
  `idContainerFormat` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Foreign key for the container format.',
  `idVideoFormat` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Foreign key for the format of the video stream within the medium.',
  `VideoFormatProfile` text COLLATE utf8_unicode_ci,
  `VideoSamplingWidth` int(10) UNSIGNED DEFAULT NULL COMMENT 'Sampling width of the video stream.',
  `VideoSamplingHeight` int(10) UNSIGNED DEFAULT NULL COMMENT 'Sampling height of the video stream.',
  `VideoBitrate` float UNSIGNED DEFAULT NULL COMMENT 'Average bitrate of the video stream, in kbit/s.',
  `VideoFramerate` float DEFAULT NULL COMMENT 'Average framerate of the video stream, in frames/s.',
  `idVideoFramerateMode` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Foreign key for the video frame rate mode.',
  `VideoQualityFactor` int(10) UNSIGNED DEFAULT NULL COMMENT 'Quality factor of the video stream.',
  `idAudioFormat` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Foreign key for the format of the audio stream within the medium.',
  `AudioFormatProfile` text COLLATE utf8_unicode_ci,
  `idAudioChannelType` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Foreign key for the channel type of the audio stream.',
  `TechnicalFlaws` text COLLATE utf8_unicode_ci COMMENT 'Any technical flaws of the movie on the medium, as very short text.\nMultiple flaws are separated by comma.\nUsually obtained from file name.\nExample: ''Size varies, Artefacts''.',
  `AudioBitrate` float DEFAULT NULL COMMENT 'Average bitrate of the audio stream, in kbit/s.',
  `idAudioBitrateMode` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Foreign key for the audio bitrate mode.',
  `AudioSamplingRate` float UNSIGNED DEFAULT NULL COMMENT 'Average sampling rate of the audio stream, in samples/s.',
  `FilePath` text COLLATE utf8_unicode_ci COMMENT 'If the medium is a file on a file server: the file name with an absolute path relative to the shared resource of the referenced media cabinet.\nOtherwise: NULL.',
  `FolderPath` text COLLATE utf8_unicode_ci COMMENT 'Folder portion of file path',
  `TSUpdated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'The time when any fields of the table row were last updated (or the row was created).',
  `TSVerified` timestamp NULL DEFAULT NULL COMMENT 'The time when the existence of the media source (e.g. file) and all fields in the table were last verified.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A movie medium (e.g. file, DVD, VHS tape).';

-- --------------------------------------------------------

--
-- Table structure for table `Movie`
--

CREATE TABLE `Movie` (
  `idMovie` int(10) UNSIGNED NOT NULL COMMENT 'Single primary key of the table.',
  `Title` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Title of the movie, in the indicated language.\nFor series: the series title, some numbering, and the episode title.',
  `ReleaseYear` year(4) DEFAULT NULL COMMENT 'The year in which the movie was released in the indicated release country in the indicated language.',
  `OriginalTitle` text COLLATE utf8_unicode_ci COMMENT 'Like Title, but the original title in the original language.',
  `SeriesTitle` text COLLATE utf8_unicode_ci COMMENT 'If the movie is part of a series, the series title, in the indicated language.\nOtherwise, NULL.',
  `OriginalSeriesTitle` text COLLATE utf8_unicode_ci COMMENT 'If the movie is part of a series, the series title, in the original language.\nOtherwise, NULL.',
  `EpisodeTitle` text COLLATE utf8_unicode_ci COMMENT 'If the movie is part of a series, the episode title, in the indicated language.\nOtherwise, NULL.',
  `OriginalEpisodeTitle` text COLLATE utf8_unicode_ci COMMENT 'If the movie is part of a series, the episode title, in the original language.\nOtherwise, NULL.',
  `EpisodeId` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'If the movie is part of a series, the episode ID (season+episode or running number). Otherwise, NULL.',
  `Duration` int(11) DEFAULT NULL COMMENT 'Official duration of the movie, in minutes.',
  `Language` varchar(3) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Language of the movie, as a 2/3 character ISO language code in lower case.',
  `OriginalLanguage` varchar(3) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Original language of the movie, as a 2/3 character ISO language code in lower case.',
  `SubtitleLanguage` varchar(3) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'If the movie has subtitles (in the display), the language of the subtitles, as a 2/3 character ISO language code in lower case. Otherwise, NULL to indicate it has no subtitles.',
  `OriginatingCountries` text COLLATE utf8_unicode_ci COMMENT 'The countries in which the movie originated, as comma separated list of german country names',
  `Genres` text COLLATE utf8_unicode_ci COMMENT 'Genres of the movie, as a comma separated list of their names.',
  `Directors` text COLLATE utf8_unicode_ci COMMENT 'Directors of the movie, as a comma separated list of their names.',
  `Actors` text COLLATE utf8_unicode_ci COMMENT 'Actors of the movie, as a comma separated list of their names.',
  `Description` text COLLATE utf8_unicode_ci COMMENT 'Brief description of the movie.\nTypically a few lines.',
  `CoverImage` blob COMMENT 'A cover image of the movie, in a portable image format (e.g. JPG, PNG, GIF).',
  `AspectRatio` float DEFAULT NULL COMMENT 'Display aspect ratio of the original movie, as a float',
  `AspectRatioStr` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Display aspect ratio of the original movie, as e.g. 16x9 or 2.35',
  `IsColored` tinyint(1) DEFAULT NULL COMMENT 'Indicates whether the movie is a color movie (vs. a black-and-white movie).',
  `IsSilent` tinyint(1) DEFAULT NULL COMMENT 'Indicates whether the movie is a silent movie.',
  `FSK` int(11) DEFAULT NULL COMMENT 'The FSK rating of the movie.',
  `IMDbLink` text COLLATE utf8_unicode_ci COMMENT 'URL of IMDb entry for the movie.',
  `IMDbRating` float UNSIGNED DEFAULT NULL COMMENT 'Rating of the movie on IMDb, from 1 (bad) to 10 (good).',
  `IMDbRaters` int(10) UNSIGNED DEFAULT NULL COMMENT 'Number of raters of the movie on IMDb.',
  `OFDbLink` text COLLATE utf8_unicode_ci COMMENT 'URL of OFDb entry for the movie.',
  `OFDbRating` float UNSIGNED DEFAULT NULL COMMENT 'Rating of the movie on OFDb, from 1 (bad) to 10 (good).',
  `OFDbRaters` int(10) UNSIGNED DEFAULT NULL COMMENT 'Number of raters of the movie on OFDb.',
  `Link` text COLLATE utf8_unicode_ci COMMENT 'URL of movie description (in addition to OFDb and IMDB links)'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A movie description.';

-- --------------------------------------------------------

--
-- Table structure for table `MovieGenre`
--

CREATE TABLE `MovieGenre` (
  `idMovieGenre` int(10) UNSIGNED NOT NULL COMMENT 'Single primary key of the table.',
  `idMovie` int(10) UNSIGNED NOT NULL COMMENT 'Foreign key to the movie.',
  `idGenre` int(10) UNSIGNED NOT NULL COMMENT 'Foreign key to the genre.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A genre of a movie.';

-- --------------------------------------------------------

--
-- Stand-in structure for view `MovieGenreView`
-- (See below for the actual view)
--
CREATE TABLE `MovieGenreView` (
`idMovieGenre` int(10) unsigned
,`idMovie` int(10) unsigned
,`idGenre` int(10) unsigned
,`GenreName` text
,`idGenreType` varchar(30)
,`GenreTypeName` text
,`idParentGenre` int(10) unsigned
,`ParentGenreName` mediumtext
,`idSynonymOfGenre` int(10) unsigned
,`SynonymOfGenreName` mediumtext
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `MovieListView`
-- (See below for the actual view)
--
CREATE TABLE `MovieListView` (
`Title` mediumtext
,`OriginalTitle` mediumtext
,`SeriesTitle` mediumtext
,`EpisodeTitle` mediumtext
,`EpisodeId` varchar(40)
,`ReleaseYear` varchar(4)
,`Duration` varchar(11)
,`Language` varchar(20)
,`Genres` mediumtext
,`Directors` mediumtext
,`Actors` mediumtext
,`Description` mediumtext
,`Quality` mediumtext
,`AspectRatio` varchar(22)
,`ContainerFormat` mediumtext
,`VideoFormat` mediumtext
,`AudioFormat` mediumtext
,`TechnicalFlaws` mediumtext
,`Status` mediumtext
,`CutStatus` varchar(5)
,`MediumType` mediumtext
,`FileLocation` mediumtext
,`IdMedium` int(10) unsigned
,`IdMovie` varchar(10)
);

-- --------------------------------------------------------

--
-- Table structure for table `MoviePerson`
--

CREATE TABLE `MoviePerson` (
  `idMoviePerson` int(10) UNSIGNED NOT NULL COMMENT 'Single primary key of the table.',
  `idMovie` int(10) UNSIGNED NOT NULL COMMENT 'Foreign key to the movie in which the person has a role.',
  `Name` text COLLATE utf8_unicode_ci NOT NULL COMMENT 'Name of the person, in normal order (e.g. first name,last name for western names)',
  `idPersonRoleType` varchar(30) COLLATE utf8_unicode_ci NOT NULL COMMENT 'Foreign key to the role the person has in the movie.'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='A person with a role in the movie (e.g. director, actor).';

-- --------------------------------------------------------

--
-- Stand-in structure for view `MoviePersonView`
-- (See below for the actual view)
--
CREATE TABLE `MoviePersonView` (
`idMoviePerson` int(10) unsigned
,`idMovie` int(10) unsigned
,`Name` text
,`idPersonRoleType` varchar(30)
,`RoleName` text
,`RoleDescription` text
);

-- --------------------------------------------------------

--
-- Table structure for table `User`
--

CREATE TABLE `User` (
  `idUser` int(11) NOT NULL,
  `NickName` varchar(30) COLLATE utf8_unicode_ci NOT NULL COMMENT 'A nickname for the user, unique in this table.',
  `FullName` text COLLATE utf8_unicode_ci COMMENT 'Full name of the user.'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='An end user (for movie statistics).';

-- --------------------------------------------------------

--
-- Table structure for table `UserMovieOpinion`
--

CREATE TABLE `UserMovieOpinion` (
  `idMovie` int(11) NOT NULL,
  `idUser` int(11) NOT NULL,
  `HasSeen` tinyint(1) DEFAULT NULL COMMENT 'Boolean indicating whether the user has actually seen the movie.',
  `Rating` int(11) DEFAULT NULL COMMENT 'Rating of the movie from the user''s perspective (1=worst, 10=best).',
  `IsRecommended` tinyint(1) DEFAULT NULL COMMENT 'Boolean indicating whether the user recommends the movie to other users.',
  `IsChristmasFilm` tinyint(1) DEFAULT NULL COMMENT 'Boolean indicating whether the film satisfies the criteria for Jutta&Andreas'' Weihnachtsfilm.'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Opinion of a user on a movie.';

-- --------------------------------------------------------

--
-- Stand-in structure for view `WeihnachtsfilmeView`
-- (See below for the actual view)
--
CREATE TABLE `WeihnachtsfilmeView` (
`Titel` mediumtext
,`Jahr` varchar(4)
,`Regie` mediumtext
,`Handlung` mediumtext
,`Sprache` varchar(20)
,`Dauer` varchar(11)
,`Qualitaet` mediumtext
,`Aspect` varchar(22)
,`Container` mediumtext
,`Video` mediumtext
,`Audio` mediumtext
,`SchnittStatus` varchar(13)
,`TechnischeMaengel` mediumtext
,`Gesehen` varchar(4)
,`File` mediumtext
);

-- --------------------------------------------------------

--
-- Structure for view `MovieGenreView`
--
DROP TABLE IF EXISTS `MovieGenreView`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `MovieGenreView`  AS  select `MovieGenre`.`idMovieGenre` AS `idMovieGenre`,`MovieGenre`.`idMovie` AS `idMovie`,`MovieGenre`.`idGenre` AS `idGenre`,`Genre`.`Name` AS `GenreName`,`Genre`.`idGenreType` AS `idGenreType`,`FixedGenreType`.`Name` AS `GenreTypeName`,`Genre`.`idParentGenre` AS `idParentGenre`,(select `_Genre`.`Name` AS `Name` from `Genre` `_Genre` where (`_Genre`.`idGenre` = `Genre`.`idParentGenre`)) AS `ParentGenreName`,`Genre`.`idSynonymOfGenre` AS `idSynonymOfGenre`,(select `_Genre`.`Name` AS `Name` from `Genre` `_Genre` where (`_Genre`.`idGenre` = `Genre`.`idSynonymOfGenre`)) AS `SynonymOfGenreName` from ((`MovieGenre` left join `Genre` on((`Genre`.`idGenre` = `MovieGenre`.`idGenre`))) left join `FixedGenreType` on((`FixedGenreType`.`idGenreType` = `Genre`.`idGenreType`))) ;

-- --------------------------------------------------------

--
-- Structure for view `MovieListView`
--
DROP TABLE IF EXISTS `MovieListView`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `MovieListView`  AS  select ifnull(`Medium`.`Title`,'') AS `Title`,ifnull(`Movie`.`OriginalTitle`,'') AS `OriginalTitle`,ifnull(`Medium`.`SeriesTitle`,'') AS `SeriesTitle`,ifnull(`Medium`.`EpisodeTitle`,'') AS `EpisodeTitle`,ifnull(`Medium`.`EpisodeId`,'') AS `EpisodeId`,ifnull(`Medium`.`ReleaseYear`,ifnull(`Movie`.`ReleaseYear`,'')) AS `ReleaseYear`,ifnull(`Medium`.`Duration`,'') AS `Duration`,ifnull(`Medium`.`Language`,'') AS `Language`,ifnull(`Movie`.`Genres`,'') AS `Genres`,ifnull(`Movie`.`Directors`,'') AS `Directors`,ifnull(`Movie`.`Actors`,'') AS `Actors`,ifnull(`Movie`.`Description`,'') AS `Description`,ifnull(`FixedQuality`.`Name`,'') AS `Quality`,concat(ifnull(`Medium`.`DesiredDisplayAspectRatioWidth`,'?'),'x',ifnull(`Medium`.`DesiredDisplayAspectRatioHeight`,'?')) AS `AspectRatio`,ifnull(`FixedContainerFormat`.`Name`,'') AS `ContainerFormat`,ifnull(`FixedVideoFormat`.`Name`,'') AS `VideoFormat`,ifnull(`FixedAudioFormat`.`Name`,'') AS `AudioFormat`,ifnull(`Medium`.`TechnicalFlaws`,'') AS `TechnicalFlaws`,ifnull(`FixedStatus`.`Name`,'') AS `Status`,if(`Medium`.`Uncut`,'Uncut','Cut') AS `CutStatus`,ifnull(`FixedMediumType`.`Name`,'') AS `MediumType`,concat('\\\\',ifnull(`Cabinet`.`SMBServerHost`,'?'),'\\',ifnull(`Cabinet`.`SMBServerShare`,'?'),ifnull(`Medium`.`FilePath`,'?')) AS `FileLocation`,`Medium`.`idMedium` AS `IdMedium`,ifnull(`Medium`.`idMovie`,'') AS `IdMovie` from ((((((((`Medium` left join `FixedMediumType` on((`FixedMediumType`.`idMediumType` = `Medium`.`idMediumType`))) left join `FixedStatus` on((`FixedStatus`.`idStatus` = `Medium`.`idStatus`))) left join `FixedQuality` on((`FixedQuality`.`idVideoQuality` = `Medium`.`idQuality`))) left join `FixedContainerFormat` on((`FixedContainerFormat`.`idContainerFormat` = `Medium`.`idContainerFormat`))) left join `FixedVideoFormat` on((`FixedVideoFormat`.`idVideoFormat` = `Medium`.`idVideoFormat`))) left join `FixedAudioFormat` on((`FixedAudioFormat`.`idAudioFormat` = `Medium`.`idAudioFormat`))) left join `Movie` on((`Movie`.`idMovie` = `Medium`.`idMovie`))) left join `Cabinet` on((`Cabinet`.`idCabinet` = `Medium`.`idCabinet`))) where ((`Medium`.`idStatus` in ('SHARED','WORK','DISABLED')) and (`Medium`.`idMediumType` = 'FILE')) order by ifnull(`Medium`.`Title`,''),ifnull(`Medium`.`ReleaseYear`,ifnull(`Movie`.`ReleaseYear`,'')) ;

-- --------------------------------------------------------

--
-- Structure for view `MoviePersonView`
--
DROP TABLE IF EXISTS `MoviePersonView`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `MoviePersonView`  AS  select `MoviePerson`.`idMoviePerson` AS `idMoviePerson`,`MoviePerson`.`idMovie` AS `idMovie`,`MoviePerson`.`Name` AS `Name`,`MoviePerson`.`idPersonRoleType` AS `idPersonRoleType`,`FixedPersonRoleType`.`Name` AS `RoleName`,`FixedPersonRoleType`.`Description` AS `RoleDescription` from (`MoviePerson` left join `FixedPersonRoleType` on((`MoviePerson`.`idPersonRoleType` = `FixedPersonRoleType`.`idPersonRoleType`))) ;

-- --------------------------------------------------------

--
-- Structure for view `WeihnachtsfilmeView`
--
DROP TABLE IF EXISTS `WeihnachtsfilmeView`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `WeihnachtsfilmeView`  AS  select ifnull(`Medium`.`Title`,'') AS `Titel`,ifnull(`Medium`.`ReleaseYear`,ifnull(`Movie`.`ReleaseYear`,'')) AS `Jahr`,ifnull(`Movie`.`Directors`,'') AS `Regie`,ifnull(`Movie`.`Description`,'') AS `Handlung`,ifnull(`Medium`.`Language`,'de') AS `Sprache`,ifnull(`Medium`.`Duration`,'') AS `Dauer`,ifnull(`FixedQuality`.`Name`,'') AS `Qualitaet`,concat(ifnull(`Medium`.`DesiredDisplayAspectRatioWidth`,'?'),'x',ifnull(`Medium`.`DesiredDisplayAspectRatioHeight`,'?')) AS `Aspect`,ifnull(`FixedContainerFormat`.`Name`,'') AS `Container`,ifnull(`FixedVideoFormat`.`Name`,'') AS `Video`,ifnull(`FixedAudioFormat`.`Name`,'') AS `Audio`,if(`Medium`.`Uncut`,'Ungeschnitten','Ok') AS `SchnittStatus`,ifnull(`Medium`.`TechnicalFlaws`,'') AS `TechnischeMaengel`,if(ifnull(`UserMovieOpinion`.`HasSeen`,0),'Ja','Nein') AS `Gesehen`,concat('\\\\',ifnull(`Cabinet`.`SMBServerHost`,'?'),'\\',ifnull(`Cabinet`.`SMBServerShare`,'?'),ifnull(`Medium`.`FilePath`,'?')) AS `File` from ((((((((`Medium` left join `Movie` on((`Movie`.`idMovie` = `Medium`.`idMovie`))) left join `Cabinet` on((`Cabinet`.`idCabinet` = `Medium`.`idCabinet`))) left join `UserMovieOpinion` on((`UserMovieOpinion`.`idMovie` = `Medium`.`idMovie`))) left join `User` on((`User`.`idUser` = `UserMovieOpinion`.`idUser`))) left join `FixedQuality` on((`FixedQuality`.`idVideoQuality` = `Medium`.`idQuality`))) left join `FixedContainerFormat` on((`FixedContainerFormat`.`idContainerFormat` = `Medium`.`idContainerFormat`))) left join `FixedVideoFormat` on((`FixedVideoFormat`.`idVideoFormat` = `Medium`.`idVideoFormat`))) left join `FixedAudioFormat` on((`FixedAudioFormat`.`idAudioFormat` = `Medium`.`idAudioFormat`))) where ((`Medium`.`idStatus` in ('SHARED','WORK','DISABLED')) and (`Medium`.`idMediumType` = 'FILE') and (`UserMovieOpinion`.`IsChristmasFilm` = 1) and (`User`.`NickName` = 'Andy')) order by ifnull(`Medium`.`Title`,''),ifnull(`Medium`.`ReleaseYear`,ifnull(`Movie`.`ReleaseYear`,'')),ifnull(`FixedQuality`.`Name`,'') ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Cabinet`
--
ALTER TABLE `Cabinet`
  ADD PRIMARY KEY (`idCabinet`),
  ADD KEY `fk_Cabinet_CabinetType` (`idCabinetType`);

--
-- Indexes for table `FixedAudioBitrateMode`
--
ALTER TABLE `FixedAudioBitrateMode`
  ADD PRIMARY KEY (`idAudioBitrateMode`);

--
-- Indexes for table `FixedAudioChannelType`
--
ALTER TABLE `FixedAudioChannelType`
  ADD PRIMARY KEY (`idAudioChannelType`);

--
-- Indexes for table `FixedAudioFormat`
--
ALTER TABLE `FixedAudioFormat`
  ADD PRIMARY KEY (`idAudioFormat`);

--
-- Indexes for table `FixedCabinetType`
--
ALTER TABLE `FixedCabinetType`
  ADD PRIMARY KEY (`idCabinetType`);

--
-- Indexes for table `FixedContainerFormat`
--
ALTER TABLE `FixedContainerFormat`
  ADD PRIMARY KEY (`idContainerFormat`);

--
-- Indexes for table `FixedGenreType`
--
ALTER TABLE `FixedGenreType`
  ADD PRIMARY KEY (`idGenreType`);

--
-- Indexes for table `FixedMediumType`
--
ALTER TABLE `FixedMediumType`
  ADD PRIMARY KEY (`idMediumType`);

--
-- Indexes for table `FixedPersonRoleType`
--
ALTER TABLE `FixedPersonRoleType`
  ADD PRIMARY KEY (`idPersonRoleType`);

--
-- Indexes for table `FixedQuality`
--
ALTER TABLE `FixedQuality`
  ADD PRIMARY KEY (`idVideoQuality`);

--
-- Indexes for table `FixedStatus`
--
ALTER TABLE `FixedStatus`
  ADD PRIMARY KEY (`idStatus`);

--
-- Indexes for table `FixedVideoFormat`
--
ALTER TABLE `FixedVideoFormat`
  ADD PRIMARY KEY (`idVideoFormat`);

--
-- Indexes for table `FixedVideoFramerateMode`
--
ALTER TABLE `FixedVideoFramerateMode`
  ADD PRIMARY KEY (`idVideoFramerateMode`);

--
-- Indexes for table `Genre`
--
ALTER TABLE `Genre`
  ADD PRIMARY KEY (`idGenre`),
  ADD KEY `fk_Genre_GenreType` (`idGenreType`),
  ADD KEY `fk_Genre_Genre` (`idSynonymOfGenre`),
  ADD KEY `fk_Genre_Genre1` (`idParentGenre`);

--
-- Indexes for table `Medium`
--
ALTER TABLE `Medium`
  ADD PRIMARY KEY (`idMedium`),
  ADD KEY `fk_Medium_Movie` (`idMovie`),
  ADD KEY `fk_Medium_Cabinet` (`idCabinet`),
  ADD KEY `fk_Medium_MediumType` (`idMediumType`),
  ADD KEY `fk_Medium_Status` (`idStatus`),
  ADD KEY `fk_Medium_Quality` (`idQuality`),
  ADD KEY `fk_Medium_FixedContainerFormat` (`idContainerFormat`),
  ADD KEY `fk_Medium_FixedVideoFormat` (`idVideoFormat`),
  ADD KEY `fk_Medium_FixedAudioFormat` (`idAudioFormat`),
  ADD KEY `fk_Medium_FixedVideoFramerateMode` (`idVideoFramerateMode`),
  ADD KEY `fk_Medium_FixedAudioBitrateMode` (`idAudioBitrateMode`),
  ADD KEY `fk_Medium_FixedAudioChannelType` (`idAudioChannelType`);

--
-- Indexes for table `Movie`
--
ALTER TABLE `Movie`
  ADD PRIMARY KEY (`idMovie`);
ALTER TABLE `Movie` ADD FULLTEXT KEY `FT_Title` (`Title`);
ALTER TABLE `Movie` ADD FULLTEXT KEY `FT_OriginalTitle` (`OriginalTitle`);

--
-- Indexes for table `MovieGenre`
--
ALTER TABLE `MovieGenre`
  ADD PRIMARY KEY (`idMovieGenre`),
  ADD KEY `fk_MovieGenre_Genre` (`idGenre`),
  ADD KEY `fk_MovieGenre_Movie` (`idMovie`);

--
-- Indexes for table `MoviePerson`
--
ALTER TABLE `MoviePerson`
  ADD PRIMARY KEY (`idMoviePerson`,`idPersonRoleType`),
  ADD KEY `fk_MoviePerson_Movie` (`idMovie`),
  ADD KEY `fk_MoviePerson_PersonRoleType` (`idPersonRoleType`);

--
-- Indexes for table `User`
--
ALTER TABLE `User`
  ADD PRIMARY KEY (`idUser`),
  ADD UNIQUE KEY `NickName` (`NickName`);

--
-- Indexes for table `UserMovieOpinion`
--
ALTER TABLE `UserMovieOpinion`
  ADD PRIMARY KEY (`idUser`,`idMovie`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Cabinet`
--
ALTER TABLE `Cabinet`
  MODIFY `idCabinet` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Single primary key of the table.', AUTO_INCREMENT=4;
--
-- AUTO_INCREMENT for table `Genre`
--
ALTER TABLE `Genre`
  MODIFY `idGenre` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=207;
--
-- AUTO_INCREMENT for table `Medium`
--
ALTER TABLE `Medium`
  MODIFY `idMedium` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Single primary key of the table.', AUTO_INCREMENT=81266;
--
-- AUTO_INCREMENT for table `Movie`
--
ALTER TABLE `Movie`
  MODIFY `idMovie` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Single primary key of the table.', AUTO_INCREMENT=4368;
--
-- AUTO_INCREMENT for table `MovieGenre`
--
ALTER TABLE `MovieGenre`
  MODIFY `idMovieGenre` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Single primary key of the table.', AUTO_INCREMENT=8961;
--
-- AUTO_INCREMENT for table `MoviePerson`
--
ALTER TABLE `MoviePerson`
  MODIFY `idMoviePerson` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Single primary key of the table.', AUTO_INCREMENT=131800;
--
-- AUTO_INCREMENT for table `User`
--
ALTER TABLE `User`
  MODIFY `idUser` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
