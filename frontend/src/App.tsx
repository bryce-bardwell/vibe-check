import { useState } from "react";
import { AppContainer, InputContainer, ResultsContainer } from "./App.styles";

type Results = {
	posts_analysed: number;
	relevant_comments: string[];
	vibe: "negative" | "neutral" | "positive";
};

function App() {
	const [topic, setTopic] = useState<string>("");
	const [results, setResults] = useState<Results | null>(null);

	const handleClick = async () => {
		const data = await fetch("http://127.0.0.1:8000/vibe", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ topic }),
		});

		const dataJson = await data.json();
		setResults(dataJson);
	};

	return (
		<AppContainer>
			<h1> Vibe Check </h1>
			<InputContainer>
				<input
					type="text"
					placeholder="The Grinch"
					value={topic}
					onChange={(e) => setTopic(e.target.value)}
				/>
				<button type="button" onClick={handleClick}>
					{" "}
					Analyse{" "}
				</button>
			</InputContainer>
			<ResultsContainer>
				<p> Vibe: {results?.vibe} </p>
				<p> Number of analysed posts: {results?.posts_analysed} </p>
				<p> Relevant comments: </p>
				<ul>
					{results?.relevant_comments.map((comment, index) => (
						<li key={index}> {comment} </li>
					))}
				</ul>
			</ResultsContainer>
		</AppContainer>
	);
}

export default App;
