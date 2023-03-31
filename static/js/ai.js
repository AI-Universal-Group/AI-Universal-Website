$(function () {
    const $loadingSpinner = $('#loading-spinner');
    const $aiOutput = $('#ai-output');
    const $promptInput = $('#prompt-input');

    function displayAiOutput(output) {
        console.log(output);
        $loadingSpinner.addClass('hidden');
        $aiOutput.text(output);
    }

    socket.on('ai-output', displayAiOutput);

    $('#ai-prompt-form').submit(function (event) {
        event.preventDefault();
        const prompt = $promptInput.val();
        $promptInput.val('');
        $loadingSpinner.removeClass('hidden');
        socket.emit('ai-prompt', prompt);
    });
});
