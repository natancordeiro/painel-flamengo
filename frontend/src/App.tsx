import DashboardPage from "./pages/DashboardPage";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <>
      <DashboardPage />
      <Toaster position="top-right" />
    </>
  );
}

export default App;
