
export default function ErrorView({errorMessage, setErrorMessage}) {
    function ackMessage(e) {
        e.stopPropagation();
        setErrorMessage(null);
    }
    return errorMessage ? <div className="error_view" onClick={ackMessage}>{errorMessage}</div> : "";
}