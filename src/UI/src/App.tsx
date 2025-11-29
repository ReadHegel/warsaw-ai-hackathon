import { ThemeProvider } from "@mui/material";
import { Chat } from "./components/Chat";
import "./index.css";
import { createTheme } from "@mui/material/styles";

export const darkTheme = createTheme({
  palette: {
    mode: "dark",
  },
});

export function App() {
  return (
      <ThemeProvider theme={darkTheme}>
        <Chat />
      </ThemeProvider>
  );
}

export default App;
