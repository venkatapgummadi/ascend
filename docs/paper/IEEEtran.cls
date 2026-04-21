%% IEEEtran.cls - Minimal IEEE LaTeX Class
%% A simplified implementation supporting IEEE journal formatting
%% Based on article class with IEEE-style modifications

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{IEEEtran}[2026/04/11 Minimal IEEE LaTeX Class]

% Class options
\newif\if@journal
\newif\if@conference
\newif\if@technote

\@journaltrue
\@conferencefalse
\@technotefalse

\DeclareOption{journal}{\@journaltrue\@conferencefalse\@technotefalse}
\DeclareOption{conference}{\@conferencefalse\@journaltrue\@technotefalse}
\DeclareOption{technote}{\@technotefalse\@conferencefalse\@journaltrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}

\ProcessOptions\relax

% Load article class as base
\LoadClass[twocolumn,11pt]{article}

% Required packages
\RequirePackage{geometry}
\RequirePackage{setspace}
\RequirePackage{graphicx}
\RequirePackage{amsmath}
\RequirePackage{amssymb}

% Page layout for journal mode
\if@journal
  \geometry{
    left=0.75in,
    right=0.75in,
    top=0.75in,
    bottom=0.75in,
    footskip=0.3in
  }
  \setlength{\columnsep}{0.25in}
\fi

% Typography settings
\setlength{\parindent}{1em}
\setlength{\parskip}{0pt}
\linespread{1.0}

% Title formatting
\renewcommand{\maketitle}{%
  \begin{center}%
    \let \footnote \thanks
    {\Large\bfseries\@title \par}%
    \vskip 1.5em%
    {\normalsize\@author \par}%
    \vskip 1.5em%
  \end{center}%
  \par
}

% Title command with extra space
\renewcommand{\title}[1]{%
  \def\@title{#1}%
}

% Author command
\renewcommand{\author}[1]{%
  \def\@author{#1}%
}

% Date command (suppress by default)
\renewcommand{\date}[1]{%
  \def\@date{#1}%
}
\date{}

% Abstract environment
\renewenvironment{abstract}{%
  \small
  \begin{center}%
    \textbf{\abstractname}%
  \end{center}%
  \quotation
}{%
  \endquotation
}

% IEEE author block commands
\newcommand{\IEEEauthorblockN}[1]{%
  {\normalsize #1}%
}

\newcommand{\IEEEauthorblockA}[1]{%
  {\small #1}%
}

% Section formatting
\renewcommand{\section}{%
  \@startsection{section}{1}{0pt}%
    {1.0ex plus 0.5ex minus 0.2ex}%
    {0.5ex plus 0.2ex}%
    {\normalsize\bfseries}%
}

\renewcommand{\subsection}{%
  \@startsection{subsection}{2}{0pt}%
    {0.8ex plus 0.4ex minus 0.2ex}%
    {0.4ex plus 0.2ex}%
    {\normalsize\itshape}%
}

\renewcommand{\subsubsection}{%
  \@startsection{subsubsection}{3}{0pt}%
    {0.6ex plus 0.3ex minus 0.2ex}%
    {0.3ex plus 0.2ex}%
    {\normalsize\itshape}%
}

% Bibliography styling
\renewcommand{\thebibliography}[1]{%
  \section*{\bibname}%
  \small
  \list{\@biblabel{\@arabic\c@enumiv}}%
    {\settowidth\labelwidth{\@biblabel{#1}}%
     \leftmargin\labelwidth
     \advance\leftmargin\labelsep
     \usecounter{enumiv}%
     \let\p@enumiv\@empty
     \renewcommand\theenumiv{\@arabic\c@enumiv}}%
  \sloppy
  \clubpenalty4000
  \@clubpenalty \clubpenalty
  \widowpenalty4000%
  \sfcode`\.\@m
}

\let\endthebibliography=\endlist

% Figure and table captions
\renewcommand{\figurename}{Figure}
\renewcommand{\tablename}{Table}

% Caption formatting
\renewcommand{\@makecaption}[2]{%
  \vskip\abovecaptionskip
  \sbox\@tempboxa{{\small\textbf{#1:} #2}}%
  \ifdim \wd\@tempboxa >\hsize
    {\small\textbf{#1:} #2\par}%
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip
}

% Paragraph formatting
\setlength{\parskip}{0pt plus 1pt}

% Header and footer
\pagestyle{plain}

% Reference for bibtex
\bibliographystyle{ieeetr}


% IEEE member designation in author field
\newcommand{\IEEEmembership}[1]{\textit{#1}}

% IEEE drop-cap first paragraph letter
\newcommand{\IEEEPARstart}[2]{\textbf{#1}#2}

% IEEE keywords environment
\newenvironment{IEEEkeywords}{%
  \par\vspace{3pt}\noindent\small\textit{Index Terms}---\ignorespaces
}{%
  \par\vspace{6pt}
}

% IEEE biography environment
\newenvironment{IEEEbiography}[2][]{%
  \vspace{6pt}\par\noindent\small\textbf{#2}~\ignorespaces
}{%
  \par\vspace{6pt}
}

% markboth for running headers (no-op in article base)
\providecommand{\markboth}[2]{}

\endinput
