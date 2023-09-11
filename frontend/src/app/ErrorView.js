
export default function ErrorView({errorMessage, setErrorMessage}) {
    function ackMessage(e) {
        e.stopPropagation();
        setErrorMessage(null);
    }
    return errorMessage ? <div onClick={ackMessage}>{errorMessage}</div> : "";
}